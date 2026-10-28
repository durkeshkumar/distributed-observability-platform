
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from shared.database import get_db
from shared.rabbitmq_publisher import publish_telemetry_event
from services.telemetry_ingestion.app.schemas.ingestion import (
    BatchEventResult,
    BatchIngestionRequest,
    BatchIngestionResponse,
    IngestionEventCreate,
    IngestionEventResponse,
)
from services.telemetry_ingestion.app.services.ingestion_service import (
    create_ingestion_event,
    get_ingestion_event_by_event_id,
    get_ingestion_statistics,
    list_ingestion_events,
    record_ingestion_attempt,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ingestion", tags=["Ingestion"])


def record_attempt_safely(
    db: Session,
    *,
    event_id: str | None,
    event_type: str | None,
    result: str,
    message: str,
) -> bool:
    try:
        record_ingestion_attempt(
            db,
            event_id=event_id,
            event_type=event_type,
            result=result,
            message=message,
        )
        return True
    except Exception:
        db.rollback()
        logger.exception(
            "Failed to record ingestion attempt: event_id=%s result=%s",
            event_id,
            result,
        )
        return False


def event_to_message(event) -> dict:
    """Convert a stored ingestion event into a JSON-safe message."""
    return {
        "event_id": event.event_id,
        "event_type": event.event_type,
        "service_name": event.service_name,
        "trace_id": event.trace_id,
        "event_timestamp": (
            event.event_timestamp.isoformat()
            if event.event_timestamp is not None
            else None
        ),
        "severity": event.severity,
        "payload": event.payload,
        "processing_status": event.processing_status,
        "error_message": event.error_message,
    }


def publish_stored_event(event) -> None:
    """Publish a stored event and surface broker failures."""
    try:
        publish_telemetry_event(event_to_message(event))
    except Exception as exc:
        logger.exception(
            "Event stored in MySQL but RabbitMQ publishing failed: "
            "event_id=%s",
            event.event_id,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Event was stored in the database, but publishing to "
                "RabbitMQ failed. Check the server logs before retrying."
            ),
        ) from exc


@router.post(
    "/events",
    response_model=IngestionEventResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_event(
    event_data: IngestionEventCreate,
    db: Session = Depends(get_db),
):
    existing = get_ingestion_event_by_event_id(db, event_data.event_id)

    if existing is not None:
        record_attempt_safely(
            db,
            event_id=event_data.event_id,
            event_type=event_data.event_type,
            result="duplicate",
            message="An event with this event_id already exists",
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An event with this event_id already exists",
        )

    try:
        event = create_ingestion_event(db, event_data)
    except IntegrityError as exc:
        db.rollback()

        existing = get_ingestion_event_by_event_id(
            db,
            event_data.event_id,
        )

        if existing is not None:
            record_attempt_safely(
                db,
                event_id=event_data.event_id,
                event_type=event_data.event_type,
                result="duplicate",
                message="An event with this event_id already exists",
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An event with this event_id already exists",
            ) from exc

        logger.exception("Database integrity error while storing event")
        record_attempt_safely(
            db,
            event_id=event_data.event_id,
            event_type=event_data.event_type,
            result="rejected",
            message="Database rejected the event",
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database rejected the event",
        ) from exc

    record_attempt_safely(
        db,
        event_id=event.event_id,
        event_type=event.event_type,
        result="accepted",
        message="Event stored successfully",
    )

    publish_stored_event(event)

    return event


@router.post(
    "/events/batch",
    response_model=BatchIngestionResponse,
    status_code=status.HTTP_200_OK,
)
def create_events_batch(
    batch: BatchIngestionRequest,
    db: Session = Depends(get_db),
):
    results: list[BatchEventResult] = []
    accepted = 0
    duplicates = 0
    rejected = 0

    for raw_event in batch.events:
        event_id = (
            raw_event.get("event_id")
            if isinstance(raw_event, dict)
            else None
        )
        event_type = (
            raw_event.get("event_type")
            if isinstance(raw_event, dict)
            else None
        )

        try:
            event_data = IngestionEventCreate.model_validate(raw_event)
        except ValidationError as exc:
            rejected += 1
            message = f"Invalid event: {exc.errors()[0]['msg']}"

            record_attempt_safely(
                db,
                event_id=event_id if isinstance(event_id, str) else None,
                event_type=event_type if isinstance(event_type, str) else None,
                result="rejected",
                message=message,
            )
            results.append(
                BatchEventResult(
                    event_id=event_id if isinstance(event_id, str) else None,
                    status="rejected",
                    message=message,
                )
            )
            continue

        existing = get_ingestion_event_by_event_id(
            db,
            event_data.event_id,
        )

        if existing is not None:
            duplicates += 1
            message = "Event already exists"

            record_attempt_safely(
                db,
                event_id=event_data.event_id,
                event_type=event_data.event_type,
                result="duplicate",
                message=message,
            )
            results.append(
                BatchEventResult(
                    event_id=event_data.event_id,
                    status="duplicate",
                    message=message,
                )
            )
            continue

        try:
            event = create_ingestion_event(db, event_data)
        except IntegrityError:
            db.rollback()

            existing = get_ingestion_event_by_event_id(
                db,
                event_data.event_id,
            )

            if existing is not None:
                duplicates += 1
                result = "duplicate"
                message = "Event already exists"
            else:
                rejected += 1
                result = "rejected"
                message = "Database rejected the event"

            record_attempt_safely(
                db,
                event_id=event_data.event_id,
                event_type=event_data.event_type,
                result=result,
                message=message,
            )
            results.append(
                BatchEventResult(
                    event_id=event_data.event_id,
                    status=result,
                    message=message,
                )
            )
            continue
        except SQLAlchemyError:
            db.rollback()
            rejected += 1
            message = "Database error while storing the event"

            logger.exception(
                "Database error during batch ingestion: event_id=%s",
                event_data.event_id,
            )
            record_attempt_safely(
                db,
                event_id=event_data.event_id,
                event_type=event_data.event_type,
                result="rejected",
                message=message,
            )
            results.append(
                BatchEventResult(
                    event_id=event_data.event_id,
                    status="rejected",
                    message=message,
                )
            )
            continue

        record_attempt_safely(
            db,
            event_id=event.event_id,
            event_type=event.event_type,
            result="accepted",
            message="Event stored successfully",
        )

        try:
            publish_stored_event(event)
        except HTTPException:
            rejected += 1
            message = (
                "Event stored in database, but RabbitMQ publishing failed"
            )
            record_attempt_safely(
                db,
                event_id=event.event_id,
                event_type=event.event_type,
                result="publish_failed",
                message=message,
            )
            results.append(
                BatchEventResult(
                    event_id=event.event_id,
                    status="rejected",
                    message=message,
                )
            )
            continue

        accepted += 1
        results.append(
            BatchEventResult(
                event_id=event.event_id,
                status="accepted",
                message="Event stored and published successfully",
            )
        )

    return BatchIngestionResponse(
        total=len(batch.events),
        accepted=accepted,
        duplicates=duplicates,
        rejected=rejected,
        results=results,
    )


@router.get(
    "/events",
    response_model=list[IngestionEventResponse],
)
def get_events(
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return list_ingestion_events(db, limit)


@router.get(
    "/events/{event_id}",
    response_model=IngestionEventResponse,
)
def get_event(
    event_id: str,
    db: Session = Depends(get_db),
):
    event = get_ingestion_event_by_event_id(db, event_id)

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ingestion event not found",
        )

    return event


@router.get("/stats", tags=["Statistics"])
def ingestion_statistics(
    db: Session = Depends(get_db),
):
    return get_ingestion_statistics(db)
