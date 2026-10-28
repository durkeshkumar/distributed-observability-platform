
from sqlalchemy import func
from sqlalchemy.orm import Session

from services.telemetry_ingestion.app.models import (
    IngestionAttempt,
    IngestionEvent,
)
from services.telemetry_ingestion.app.schemas.ingestion import (
    IngestionEventCreate,
)


def create_ingestion_event(
    db: Session,
    event_data: IngestionEventCreate,
) -> IngestionEvent:
    event = IngestionEvent(
        event_id=event_data.event_id,
        event_type=event_data.event_type,
        service_name=event_data.service_name,
        trace_id=event_data.trace_id,
        event_timestamp=event_data.event_timestamp,
        severity=event_data.severity,
        payload=event_data.payload,
        processing_status=event_data.processing_status,
        error_message=event_data.error_message,
    )

    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def get_ingestion_event_by_event_id(
    db: Session,
    event_id: str,
) -> IngestionEvent | None:
    return (
        db.query(IngestionEvent)
        .filter(IngestionEvent.event_id == event_id)
        .first()
    )


def list_ingestion_events(
    db: Session,
    limit: int = 100,
) -> list[IngestionEvent]:
    return (
        db.query(IngestionEvent)
        .order_by(IngestionEvent.id.desc())
        .limit(limit)
        .all()
    )


def record_ingestion_attempt(
    db: Session,
    *,
    event_id: str | None,
    event_type: str | None,
    result: str,
    message: str,
) -> None:
    attempt = IngestionAttempt(
        event_id=event_id,
        event_type=event_type,
        result=result,
        message=message,
    )

    db.add(attempt)
    db.commit()


def get_ingestion_statistics(db: Session) -> dict:
    total_events = (
        db.query(func.count(IngestionEvent.id)).scalar() or 0
    )

    type_rows = (
        db.query(
            IngestionEvent.event_type,
            func.count(IngestionEvent.id),
        )
        .group_by(IngestionEvent.event_type)
        .all()
    )

    status_rows = (
        db.query(
            IngestionEvent.processing_status,
            func.count(IngestionEvent.id),
        )
        .group_by(IngestionEvent.processing_status)
        .all()
    )

    attempt_rows = (
        db.query(
            IngestionAttempt.result,
            func.count(IngestionAttempt.id),
        )
        .group_by(IngestionAttempt.result)
        .all()
    )

    attempts_by_result = {
        result: count for result, count in attempt_rows
    }

    return {
        "total_events": total_events,
        "events_by_type": {
            event_type: count for event_type, count in type_rows
        },
        "events_by_status": {
            event_status: count for event_status, count in status_rows
        },
        "total_attempts": sum(attempts_by_result.values()),
        "attempts_by_result": attempts_by_result,
    }
