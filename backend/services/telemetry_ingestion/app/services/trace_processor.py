
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from services.telemetry_ingestion.app.models import TraceSpan


def parse_datetime(value: Any, field_name: str) -> datetime:
    """Parse a timestamp and normalize it to UTC without timezone info."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty ISO timestamp")

    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field_name} must be a valid ISO timestamp") from exc

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)

    return parsed.astimezone(timezone.utc).replace(tzinfo=None)


def process_trace_event(db: Session, event: dict[str, Any]) -> TraceSpan:
    """Validate and persist one trace event as a span."""
    if event.get("event_type") != "trace":
        raise ValueError("Only trace events can be processed here")

    trace_id = event.get("trace_id")
    service_name = event.get("service_name")
    payload = event.get("payload")

    if not isinstance(trace_id, str) or not trace_id.strip():
        raise ValueError("Trace event requires a valid trace_id")

    if not isinstance(service_name, str) or not service_name.strip():
        raise ValueError("Trace event requires a valid service_name")

    if not isinstance(payload, dict):
        raise ValueError("Trace event payload must be a JSON object")

    span_id = payload.get("span_id")
    operation = payload.get("operation")
    parent_span_id = payload.get("parent_span_id")

    if not isinstance(span_id, str) or not span_id.strip():
        raise ValueError("Trace payload requires a valid span_id")

    if not isinstance(operation, str) or not operation.strip():
        raise ValueError("Trace payload requires a valid operation")

    if parent_span_id is not None:
        if not isinstance(parent_span_id, str) or not parent_span_id.strip():
            raise ValueError("parent_span_id must be a non-empty string or null")
        parent_span_id = parent_span_id.strip()

    start_value = payload.get("start_time") or event.get("event_timestamp")
    if start_value is None:
        raise ValueError("Trace payload requires start_time or event_timestamp")

    start_time = parse_datetime(start_value, "start_time")
    end_value = payload.get("end_time")
    end_time = parse_datetime(end_value, "end_time") if end_value is not None else None

    if end_time is not None and end_time < start_time:
        raise ValueError("end_time cannot be earlier than start_time")

    duration_ms = (
        (end_time - start_time).total_seconds() * 1000
        if end_time is not None
        else None
    )

    status = payload.get("status", "UNSET")
    if not isinstance(status, str) or not status.strip():
        raise ValueError("Trace status must be a non-empty string")

    span = TraceSpan(
        trace_id=trace_id.strip(),
        span_id=span_id.strip(),
        parent_span_id=parent_span_id,
        service_name=service_name.strip(),
        operation_name=operation.strip(),
        start_time=start_time,
        end_time=end_time,
        duration_ms=duration_ms,
        status=status.strip().upper(),
    )

    try:
        db.add(span)
        db.commit()
        db.refresh(span)
        return span
    except IntegrityError:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise
