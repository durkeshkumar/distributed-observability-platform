
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from services.telemetry_ingestion.app.models import (
    LogRecord,
    MetricRecord,
    TraceSpan,
)


def correlate_trace_telemetry(
    db: Session,
    trace_id: str,
    metric_window_seconds: int = 300,
) -> dict:
    """
    Gather trace spans, logs linked by trace_id, and metrics
    from the services involved in the trace.

    Metrics are selected by service name and timestamp proximity.
    """

    if not trace_id or not trace_id.strip():
        raise ValueError("trace_id must not be empty")

    if metric_window_seconds < 0:
        raise ValueError("metric_window_seconds must not be negative")

    spans = (
        db.query(TraceSpan)
        .filter(TraceSpan.trace_id == trace_id)
        .order_by(TraceSpan.start_time.asc(), TraceSpan.id.asc())
        .all()
    )

    if not spans:
        return {
            "trace_id": trace_id,
            "span_count": 0,
            "log_count": 0,
            "metric_count": 0,
            "spans": [],
            "logs": [],
            "metrics": [],
            "services": [],
        }

    service_names = sorted({span.service_name for span in spans})

    logs = (
        db.query(LogRecord)
        .filter(
            LogRecord.trace_id == trace_id,
            LogRecord.service_name.in_(service_names),
        )
        .order_by(LogRecord.timestamp.asc(), LogRecord.id.asc())
        .all()
    )

    earliest_start = min(span.start_time for span in spans)
    latest_end = max(
        (span.end_time or span.start_time) for span in spans
    )

    window_start = earliest_start - timedelta(
        seconds=metric_window_seconds
    )
    window_end = latest_end + timedelta(
        seconds=metric_window_seconds
    )

    metrics = (
        db.query(MetricRecord)
        .filter(
            MetricRecord.service_name.in_(service_names),
            MetricRecord.timestamp >= window_start,
            MetricRecord.timestamp <= window_end,
        )
        .order_by(MetricRecord.timestamp.asc(), MetricRecord.id.asc())
        .all()
    )

    return {
        "trace_id": trace_id,
        "span_count": len(spans),
        "log_count": len(logs),
        "metric_count": len(metrics),
        "services": service_names,
        "spans": [
            {
                "id": span.id,
                "trace_id": span.trace_id,
                "span_id": span.span_id,
                "parent_span_id": span.parent_span_id,
                "service_name": span.service_name,
                "operation_name": span.operation_name,
                "start_time": span.start_time,
                "end_time": span.end_time,
                "duration_ms": span.duration_ms,
                "status": span.status,
            }
            for span in spans
        ],
        "logs": [
            {
                "id": log.id,
                "event_id": log.event_id,
                "service_name": log.service_name,
                "message": log.message,
                "severity": log.severity,
                "timestamp": log.timestamp,
                "trace_id": log.trace_id,
                "attributes": log.attributes,
            }
            for log in logs
        ],
        "metrics": [
            {
                "id": metric.id,
                "event_id": metric.event_id,
                "service_name": metric.service_name,
                "metric_name": metric.metric_name,
                "metric_type": metric.metric_type,
                "value": metric.value,
                "unit": metric.unit,
                "timestamp": metric.timestamp,
                "attributes": metric.attributes,
            }
            for metric in metrics
        ],
    }
