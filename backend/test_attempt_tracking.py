
from unittest.mock import MagicMock, patch

import pytest

from services.telemetry_ingestion.app.services.ingestion_service import (
    record_ingestion_attempt,
)


@patch(
    "services.telemetry_ingestion.app.services.ingestion_service.IngestionAttempt"
)
def test_record_ingestion_attempt_saves_duplicate_result(
    mock_attempt_model,
):
    db = MagicMock()
    mock_attempt = MagicMock()
    mock_attempt_model.return_value = mock_attempt

    result = record_ingestion_attempt(
        db,
        event_id="pytest-attempt-001",
        event_type="log",
        result="duplicate",
        message="Duplicate event detected",
    )

    assert result is None
    mock_attempt_model.assert_called_once_with(
        event_id="pytest-attempt-001",
        event_type="log",
        result="duplicate",
        message="Duplicate event detected",
    )
    db.add.assert_called_once_with(mock_attempt)
    db.commit.assert_called_once_with()


@patch(
    "services.telemetry_ingestion.app.services.ingestion_service.IngestionAttempt"
)
def test_record_ingestion_attempt_accepts_optional_event_fields(
    mock_attempt_model,
):
    db = MagicMock()

    record_ingestion_attempt(
        db,
        event_id=None,
        event_type=None,
        result="rejected",
        message="Event could not be identified",
    )

    mock_attempt_model.assert_called_once_with(
        event_id=None,
        event_type=None,
        result="rejected",
        message="Event could not be identified",
    )
    db.add.assert_called_once()
    db.commit.assert_called_once()


@patch(
    "services.telemetry_ingestion.app.services.ingestion_service.IngestionAttempt"
)
def test_record_ingestion_attempt_propagates_commit_failure(
    mock_attempt_model,
):
    db = MagicMock()
    db.commit.side_effect = RuntimeError("Database commit failed")

    with pytest.raises(RuntimeError, match="Database commit failed"):
        record_ingestion_attempt(
            db,
            event_id="pytest-attempt-003",
            event_type="metric",
            result="failed",
            message="Test database failure",
        )

    db.add.assert_called_once()
    db.commit.assert_called_once()
