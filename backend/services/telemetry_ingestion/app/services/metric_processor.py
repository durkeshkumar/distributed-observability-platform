
from sqlalchemy.orm import Session

from services.telemetry_ingestion.app.models import MetricRecord
from services.telemetry_ingestion.app.services.metric_validator import (
    MetricEvent,
)


def process_metric_event(
    db: Session,
    event_data: dict,
) -> MetricRecord:
    """Validate and persist a metric event."""

    metric = MetricEvent.model_validate(event_data)

    existing = (
        db.query(MetricRecord)
        .filter(MetricRecord.event_id == metric.event_id)
        .first()
    )

    if existing:
        raise ValueError(
            f"Metric event already exists: {metric.event_id}"
        )

    record = MetricRecord(
        event_id=metric.event_id,
        service_name=metric.service_name,
        metric_name=metric.metric_name,
        metric_type=metric.metric_type,
        value=metric.value,
        unit=metric.unit,
        timestamp=metric.timestamp,
        attributes=metric.attributes,
    )

    try:
        db.add(record)
        db.commit()
        db.refresh(record)
    except Exception:
        db.rollback()
        raise

    return record
