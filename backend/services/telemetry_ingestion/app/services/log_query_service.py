
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from services.telemetry_ingestion.app.models import LogRecord


def list_logs(
    db: Session,
    *,
    service_name: str | None = None,
    severity: str | None = None,
    trace_id: str | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[int, list[LogRecord]]:
    """Return filtered log records with pagination."""

    query = db.query(LogRecord)

    if service_name:
        query = query.filter(
            LogRecord.service_name == service_name
        )

    if severity:
        query = query.filter(
            LogRecord.severity == severity.upper()
        )

    if trace_id:
        query = query.filter(
            LogRecord.trace_id == trace_id
        )

    if start_time:
        query = query.filter(
            LogRecord.timestamp >= start_time
        )

    if end_time:
        query = query.filter(
            LogRecord.timestamp <= end_time
        )

    total = query.with_entities(
        func.count(LogRecord.id)
    ).scalar() or 0

    items = (
        query.order_by(
            LogRecord.timestamp.desc(),
            LogRecord.id.desc(),
        )
        .offset(offset)
        .limit(limit)
        .all()
    )

    return total, items


def get_log_by_id(
    db: Session,
    log_id: int,
) -> LogRecord | None:
    """Return one log record by its database ID."""

    return (
        db.query(LogRecord)
        .filter(LogRecord.id == log_id)
        .first()
    )
