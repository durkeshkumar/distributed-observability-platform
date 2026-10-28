
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.exc import IntegrityError

from services.telemetry_ingestion.app.services.log_processor import (
    parse_log_timestamp,
    process_log_event,
)


@pytest.fixture
def valid_log_event():
    return {
        "event_type": "log",
        "event_id": "pytest-log-001",
        "service_name": "order-service",
        "trace_id": "pytest-trace-001",
        "severity": "INFO",
        "event_timestamp": "2026-10-17T10:00:00Z",
        "payload": {
            "message": "Test log event",
            "timestamp": "2026-10-17T10:00:00Z",
            "attributes": {"environment": "test"},
        },
    }


@patch(
    "services.telemetry_ingestion.app.services.log_processor.LogRecord"
)
def test_process_log_event_saves_valid_log(
    mock_log_model, valid_log_event
):
    db = MagicMock()
    mock_record = MagicMock()
    mock_log_model.return_value = mock_record

    result = process_log_event(db, valid_log_event)

    assert result is mock_record
    mock_log_model.assert_called_once_with(
        event_id="pytest-log-001",
        service_name="order-service",
        message="Test log event",
        severity="INFO",
        timestamp=datetime(2026, 10, 17, 10, 0, 0),
        trace_id="pytest-trace-001",
        attributes={"environment": "test"},
    )
    db.add.assert_called_once_with(mock_record)
    db.commit.assert_called_once_with()
    db.refresh.assert_called_once_with(mock_record)
    db.rollback.assert_not_called()


@pytest.mark.parametrize(
    ("field", "value", "error_message"),
    [
        ("event_type", "metric", "Only log events can be processed"),
        ("event_id", "", "valid event_id"),
        ("service_name", "", "valid service_name"),
        ("payload", None, "payload must be a JSON object"),
    ],
)
def test_process_log_event_rejects_invalid_fields(
    valid_log_event, field, value, error_message
):
    db = MagicMock()
    valid_log_event[field] = value

    with pytest.raises(ValueError, match=error_message):
        process_log_event(db, valid_log_event)

    db.add.assert_not_called()
    db.commit.assert_not_called()


def test_process_log_event_rejects_missing_message(valid_log_event):
    db = MagicMock()
    valid_log_event["payload"]["message"] = " "

    with pytest.raises(ValueError, match="non-empty message"):
        process_log_event(db, valid_log_event)

    db.add.assert_not_called()
    db.commit.assert_not_called()


def test_process_log_event_normalizes_warn_severity(valid_log_event):
    db = MagicMock()
    valid_log_event["severity"] = "warn"

    with patch(
        "services.telemetry_ingestion.app.services.log_processor.LogRecord"
    ) as mock_log_model:
        mock_record = MagicMock()
        mock_log_model.return_value = mock_record

        result = process_log_event(db, valid_log_event)

    assert result is mock_record
    assert mock_log_model.call_args.kwargs["severity"] == "WARNING"
    db.commit.assert_called_once_with()


def test_process_log_event_rolls_back_on_integrity_error(
    valid_log_event,
):
    db = MagicMock()
    db.commit.side_effect = IntegrityError(
        "INSERT", {}, Exception("Duplicate event")
    )

    with pytest.raises(IntegrityError):
        process_log_event(db, valid_log_event)

    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.rollback.assert_called_once()


def test_process_log_event_rolls_back_on_unexpected_error(
    valid_log_event,
):
    db = MagicMock()
    db.commit.side_effect = RuntimeError("Database unavailable")

    with pytest.raises(RuntimeError, match="Database unavailable"):
        process_log_event(db, valid_log_event)

    db.rollback.assert_called_once()


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("2026-10-17T10:00:00Z", datetime(2026, 10, 17, 10, 0, 0)),
        (
            "2026-10-17T12:00:00+02:00",
            datetime(2026, 10, 17, 10, 0, 0),
        ),
        ("2026-10-17T10:00:00", datetime(2026, 10, 17, 10, 0, 0)),
    ],
)
def test_parse_log_timestamp_normalizes_to_utc(value, expected):
    assert parse_log_timestamp(value) == expected


@pytest.mark.parametrize(
    "value",
    [None, "", "not-a-timestamp"],
)
def test_parse_log_timestamp_rejects_invalid_values(value):
    with pytest.raises(ValueError, match="Log timestamp"):
        parse_log_timestamp(value)
