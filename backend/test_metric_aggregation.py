
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from services.telemetry_ingestion.app.services.metric_aggregation_service import (
    get_request_count,
    get_error_rate,
    get_average_latency,
    group_metrics_by_service,
)


def make_query_mock(db):
    """Create a reusable mock for chained SQLAlchemy queries."""
    query = MagicMock()
    db.query.return_value = query
    query.filter.return_value = query
    query.group_by.return_value = query
    query.order_by.return_value = query
    return query


def test_get_request_count_returns_total():
    db = MagicMock()
    query = make_query_mock(db)
    query.scalar.return_value = 25

    result = get_request_count(db, service_name="order-service")

    assert result == 25.0
    assert query.filter.call_count == 2


def test_get_request_count_returns_zero_when_no_records():
    db = MagicMock()
    query = make_query_mock(db)
    query.scalar.return_value = None

    result = get_request_count(db, service_name="order-service")

    assert result == 0.0


def test_get_error_rate_calculates_percentage():
    db = MagicMock()
    query = make_query_mock(db)
    query.scalar.side_effect = [200, 10]

    result = get_error_rate(db, service_name="order-service")

    assert result == 5.0
    assert query.filter.call_count == 2


def test_get_error_rate_returns_none_when_no_requests():
    db = MagicMock()
    query = make_query_mock(db)
    query.scalar.side_effect = [0, 0]

    result = get_error_rate(db, service_name="order-service")

    assert result is None


def test_get_average_latency_returns_average():
    db = MagicMock()
    query = make_query_mock(db)
    query.scalar.return_value = 125.5

    result = get_average_latency(db, service_name="order-service")

    assert result == 125.5


def test_get_average_latency_returns_none_when_no_records():
    db = MagicMock()
    query = make_query_mock(db)
    query.scalar.return_value = None

    result = get_average_latency(db, service_name="order-service")

    assert result is None


def test_group_metrics_by_service_returns_summaries():
    db = MagicMock()
    query = make_query_mock(db)

    rows = [
        SimpleNamespace(
            service_name="order-service",
            metric_name="request_count",
            record_count=3,
            total_value=30,
            average_value=10,
        ),
        SimpleNamespace(
            service_name="payment-service",
            metric_name="error_count",
            record_count=2,
            total_value=None,
            average_value=None,
        ),
    ]
    query.all.return_value = rows

    result = group_metrics_by_service(db)

    assert result == [
        {
            "service_name": "order-service",
            "metric_name": "request_count",
            "record_count": 3,
            "total_value": 30.0,
            "average_value": 10.0,
        },
        {
            "service_name": "payment-service",
            "metric_name": "error_count",
            "record_count": 2,
            "total_value": 0.0,
            "average_value": None,
        },
    ]


def test_group_metrics_by_service_returns_empty_list():
    db = MagicMock()
    query = make_query_mock(db)
    query.all.return_value = []

    result = group_metrics_by_service(db)

    assert result == []


@pytest.mark.parametrize("metric_value", [0, None])
def test_get_request_count_handles_empty_or_zero_values(metric_value):
    db = MagicMock()
    query = make_query_mock(db)
    query.scalar.return_value = metric_value

    result = get_request_count(db, service_name="order-service")

    assert result == 0.0
