
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session

from shared.database import get_db
from services.telemetry_ingestion.app.schemas.log import (
    LogListResponse,
    LogRecordResponse,
)
from services.telemetry_ingestion.app.services.log_query_service import (
    get_log_by_id,
    list_logs,
)

router = APIRouter(prefix="/logs", tags=["Logs"])


@router.get("", response_model=LogListResponse)
def get_logs(
    service_name: str | None = Query(default=None, min_length=1),
    severity: str | None = Query(default=None, min_length=1),
    trace_id: str | None = Query(default=None, min_length=1),
    start_time: datetime | None = Query(default=None),
    end_time: datetime | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    """List stored logs with optional filters and pagination."""

    if start_time and end_time and start_time > end_time:
        raise HTTPException(
            status_code=422,
            detail="start_time must be earlier than or equal to end_time",
        )

    normalized_severity = severity.upper() if severity else None

    if normalized_severity == "WARN":
        normalized_severity = "WARNING"

    total, items = list_logs(
        db,
        service_name=service_name,
        severity=normalized_severity,
        trace_id=trace_id,
        start_time=start_time,
        end_time=end_time,
        limit=limit,
        offset=offset,
    )

    return LogListResponse(
        total=total,
        limit=limit,
        offset=offset,
        items=items,
    )


@router.get("/{log_id}", response_model=LogRecordResponse)
def get_log(
    log_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
):
    """Retrieve a stored log by its database ID."""

    log_record = get_log_by_id(db, log_id)

    if log_record is None:
        raise HTTPException(
            status_code=404,
            detail="Log record not found",
        )

    return log_record
