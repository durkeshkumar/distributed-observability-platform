
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from services.telemetry_ingestion.app.models import MetricRecord


def list_metrics(
    db: Session,
    *,
    service_name: str | None = None,
    metric_name: str | None = None,
    metric_type: str | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[int, list[MetricRecord]]:
    """List metric records with filters and pagination."""

    query = db.query(MetricRecord)

    if service_name:
        query = query.filter(
            MetricRecord.service_name == service_name
        )

    if metric_name:
        query = query.filter(
            MetricRecord.metric_name == metric_name
        )

    if metric_type:
        query = query.filter(
            MetricRecord.metric_type == metric_type.lower()
        )

    if start_time:
        query = query.filter(
            MetricRecord.timestamp >= start_time
        )

    if end_time:
        query = query.filter(
            MetricRecord.timestamp <= end_time
        )

    total = query.with_entities(
        func.count(MetricRecord.id)
    ).scalar() or 0

    items = (
        query.order_by(
            MetricRecord.timestamp.desc(),
            MetricRecord.id.desc(),
        )
        .offset(offset)
        .limit(limit)
        .all()
    )

    return total, items


def get_metric_by_id(
    db: Session,
    metric_id: int,
) -> MetricRecord | None:
    """Retrieve a metric record by database ID."""

    return (
        db.query(MetricRecord)
        .filter(MetricRecord.id == metric_id)
        .first()
    )
