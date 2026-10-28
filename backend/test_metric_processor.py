
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from services.telemetry_ingestion.app.models import MetricRecord
from services.telemetry_ingestion.app.services.metric_processor import (
    process_metric_event,
)


@pytest.fixture
def valid_metric_event():
    return {
        "event_id": "pytest-metric-test-001",
        "service_name": "order-service",
        "metric_name": "request_count",
        "metric_type": "counter",
        "value": 10,
        "unit": "requests",
        "timestamp": datetime(2026, 10, 17, 10, 0, 0),
        "attributes": {
            "environment": "test",
            "test": True,
        },
    }


def test_process_metric_event_saves_valid_metric(valid_metric_event):
    db = MagicMock()

    # Simulate no existing metric with the same event ID.
    db.query.return_value.filter.return_value.first.return_value = None

    with patch(
        "services.telemetry_ingestion.app.services.metric_processor.MetricRecord"
    ) as mock_metric_model:
        mock_record = MagicMock()
        mock_metric_model.return_value = mock_record

        result = process_metric_event(db, valid_metric_event)

    assert result is mock_record
    db.add.assert_called_once_with(mock_record)
    db.commit.assert_called_once_with()
    db.refresh.assert_called_once_with(mock_record)
    db.rollback.assert_not_called()


def test_process_metric_event_rejects_duplicate(valid_metric_event):
    db = MagicMock()
    existing_record = MagicMock()

    db.query.return_value.filter.return_value.first.return_value = (
        existing_record
    )

    with pytest.raises(ValueError, match="Metric event already exists"):
        process_metric_event(db, valid_metric_event)

    db.add.assert_not_called()
    db.commit.assert_not_called()


def test_process_metric_event_rejects_missing_event_id(valid_metric_event):
    valid_metric_event.pop("event_id")
    db = MagicMock()

    with pytest.raises(ValueError):
        process_metric_event(db, valid_metric_event)

    db.add.assert_not_called()
    db.commit.assert_not_called()


def test_process_metric_event_rolls_back_on_commit_failure(
    valid_metric_event,
):
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None
    db.commit.side_effect = RuntimeError("Database commit failed")

    with pytest.raises(RuntimeError, match="Database commit failed"):
        process_metric_event(db, valid_metric_event)

    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.rollback.assert_called_once()
