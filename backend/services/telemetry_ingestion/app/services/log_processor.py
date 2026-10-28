
from datetime import datetime, timezone
from math import isfinite
from typing import Any

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from services.telemetry_ingestion.app.models import LogRecord


VALID_SEVERITIES = {
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
}


def parse_log_timestamp(value: Any) -> datetime:
    """Parse a log timestamp and normalize it to UTC without timezone info."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Log timestamp must be a non-empty ISO timestamp")

    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("Log timestamp must be a valid ISO timestamp") from exc

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)

    return parsed.astimezone(timezone.utc).replace(tzinfo=None)


def process_log_event(db: Session, event: dict[str, Any]) -> LogRecord:
    """Validate and persist one log event."""
    if event.get("event_type") != "log":
        raise ValueError("Only log events can be processed here")

    event_id = event.get("event_id")
    service_name = event.get("service_name")
    payload = event.get("payload")

    if not isinstance(event_id, str) or not event_id.strip():
        raise ValueError("Log event requires a valid event_id")

    if not isinstance(service_name, str) or not service_name.strip():
        raise ValueError("Log event requires a valid service_name")

    if not isinstance(payload, dict):
        raise ValueError("Log event payload must be a JSON object")

    message = payload.get("message")

    if not isinstance(message, str) or not message.strip():
        raise ValueError("Log payload requires a non-empty message")

    severity_value = event.get("severity") or payload.get("severity") or "INFO"

    if not isinstance(severity_value, str):
        raise ValueError("Log severity must be a string")

    severity = severity_value.strip().upper()

    if severity == "WARN":
        severity = "WARNING"

    if severity not in VALID_SEVERITIES:
        raise ValueError(
            f"Unsupported log severity: {severity_value!r}. "
            f"Allowed values: {', '.join(sorted(VALID_SEVERITIES))}"
        )

    timestamp_value = (
        payload.get("timestamp")
        or payload.get("start_time")
        or event.get("event_timestamp")
    )

    timestamp = parse_log_timestamp(timestamp_value)

    trace_id = event.get("trace_id")

    if trace_id is not None:
        if not isinstance(trace_id, str) or not trace_id.strip():
            raise ValueError("trace_id must be a non-empty string or null")
        trace_id = trace_id.strip()

    attributes = payload.get("attributes")

    if attributes is not None and not isinstance(attributes, dict):
        raise ValueError("Log attributes must be a JSON object or null")

    record = LogRecord(
        event_id=event_id.strip(),
        service_name=service_name.strip(),
        message=message.strip(),
        severity=severity,
        timestamp=timestamp,
        trace_id=trace_id,
        attributes=attributes,
    )

    try:
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    except IntegrityError:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise
