
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from services.telemetry_ingestion.app.models import MetricRecord


def get_request_count(
    db: Session,
    *,
    service_name: str | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
) -> float:
    """Sum recorded request_count metric values."""

    query = db.query(
        func.coalesce(func.sum(MetricRecord.value), 0)
    ).filter(
        MetricRecord.metric_name == "request_count"
    )

    if service_name:
        query = query.filter(
            MetricRecord.service_name == service_name
        )

    if start_time:
        query = query.filter(
            MetricRecord.timestamp >= start_time
        )

    if end_time:
        query = query.filter(
            MetricRecord.timestamp <= end_time
        )

    return float(query.scalar() or 0)


def get_error_rate(
    db: Session,
    *,
    service_name: str,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
) -> float | None:
    """Calculate error_count / request_count * 100.

    Returns None when no requests were recorded.
    Assumes error_count and request_count are comparable counters.
    """

    common_filters = [
        MetricRecord.service_name == service_name,
    ]

    if start_time:
        common_filters.append(
            MetricRecord.timestamp >= start_time
        )

    if end_time:
        common_filters.append(
            MetricRecord.timestamp <= end_time
        )

    request_count = (
        db.query(func.coalesce(func.sum(MetricRecord.value), 0))
        .filter(
            *common_filters,
            MetricRecord.metric_name == "request_count",
        )
        .scalar()
    )

    error_count = (
        db.query(func.coalesce(func.sum(MetricRecord.value), 0))
        .filter(
            *common_filters,
            MetricRecord.metric_name == "error_count",
        )
        .scalar()
    )

    if not request_count:
        return None

    return float(error_count or 0) / float(request_count) * 100


def get_average_latency(
    db: Session,
    *,
    service_name: str | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
) -> float | None:
    """Return average recorded request_latency values."""

    query = db.query(
        func.avg(MetricRecord.value)
    ).filter(
        MetricRecord.metric_name == "request_latency"
    )

    if service_name:
        query = query.filter(
            MetricRecord.service_name == service_name
        )

    if start_time:
        query = query.filter(
            MetricRecord.timestamp >= start_time
        )

    if end_time:
        query = query.filter(
            MetricRecord.timestamp <= end_time
        )

    result = query.scalar()

    return float(result) if result is not None else None


def group_metrics_by_service(
    db: Session,
    *,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
) -> list[dict]:
    """Summarize metric values by service and metric name."""

    query = db.query(
        MetricRecord.service_name.label("service_name"),
        MetricRecord.metric_name.label("metric_name"),
        func.count(MetricRecord.id).label("record_count"),
        func.sum(MetricRecord.value).label("total_value"),
        func.avg(MetricRecord.value).label("average_value"),
    )

    if start_time:
        query = query.filter(
            MetricRecord.timestamp >= start_time
        )

    if end_time:
        query = query.filter(
            MetricRecord.timestamp <= end_time
        )

    rows = (
        query.group_by(
            MetricRecord.service_name,
            MetricRecord.metric_name,
        )
        .order_by(
            MetricRecord.service_name,
            MetricRecord.metric_name,
        )
        .all()
    )

    return [
        {
            "service_name": row.service_name,
            "metric_name": row.metric_name,
            "record_count": row.record_count,
            "total_value": (
                float(row.total_value)
                if row.total_value is not None
                else 0.0
            ),
            "average_value": (
                float(row.average_value)
                if row.average_value is not None
                else None
            ),
        }
        for row in rows
    ]
