
import json
from unittest.mock import MagicMock, patch

import pytest

from shared.rabbitmq_publisher import publish_telemetry_event


@pytest.fixture
def test_event():
    return {
        "event_id": "rabbitmq-publish-test-001",
        "event_type": "log",
        "service_name": "publisher-test",
        "trace_id": "rabbitmq-test-trace-001",
        "severity": "INFO",
        "payload": {
            "message": "Testing telemetry publishing to RabbitMQ"
        },
    }


@pytest.fixture
def rabbitmq_mocks():
    connection = MagicMock()
    channel = MagicMock()

    connection.is_open = True
    connection.channel.return_value = channel
    channel.is_open = True
    channel.basic_publish.return_value = True

    with (
        patch(
            "shared.rabbitmq_publisher.get_rabbitmq_connection",
            return_value=connection,
        ) as mock_get_connection,
        patch(
            "shared.rabbitmq_publisher.declare_telemetry_queue"
        ) as mock_declare_queue,
        patch(
            "shared.rabbitmq_publisher.pika.BasicProperties"
        ) as mock_properties,
    ):
        yield {
            "connection": connection,
            "channel": channel,
            "get_connection": mock_get_connection,
            "declare_queue": mock_declare_queue,
            "properties": mock_properties,
        }


def test_publish_telemetry_event_success(test_event, rabbitmq_mocks):
    mocks = rabbitmq_mocks

    result = publish_telemetry_event(test_event)

    assert result is True
    mocks["get_connection"].assert_called_once_with()
    mocks["declare_queue"].assert_called_once_with(mocks["connection"])
    mocks["connection"].channel.assert_called_once_with()
    mocks["channel"].confirm_delivery.assert_called_once_with()

    publish_kwargs = mocks["channel"].basic_publish.call_args.kwargs

    assert publish_kwargs["exchange"] == ""
    assert publish_kwargs["routing_key"] == "telemetry_events"
    assert publish_kwargs["body"] == json.dumps(
        test_event,
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    assert publish_kwargs["mandatory"] is True

    mocks["properties"].assert_called_once_with(
        content_type="application/json",
        delivery_mode=2,
        message_id=test_event["event_id"],
    )

    assert publish_kwargs["properties"] is mocks["properties"].return_value
    mocks["channel"].close.assert_called_once_with()
    mocks["connection"].close.assert_called_once_with()


@pytest.mark.parametrize("event_id", ["", "   ", None, 123])
def test_publish_rejects_invalid_event_id(event_id, rabbitmq_mocks, test_event):
    test_event["event_id"] = event_id

    with pytest.raises(ValueError, match="valid event_id"):
        publish_telemetry_event(test_event)

    rabbitmq_mocks["get_connection"].assert_not_called()


def test_publish_raises_when_broker_does_not_confirm(
    test_event, rabbitmq_mocks
):
    rabbitmq_mocks["channel"].basic_publish.return_value = False

    with pytest.raises(RuntimeError, match="did not confirm event"):
        publish_telemetry_event(test_event)

    rabbitmq_mocks["channel"].close.assert_called_once_with()
    rabbitmq_mocks["connection"].close.assert_called_once_with()


def test_publish_cleans_up_after_publish_exception(
    test_event, rabbitmq_mocks
):
    rabbitmq_mocks["channel"].basic_publish.side_effect = RuntimeError(
        "Publish failed"
    )

    with pytest.raises(RuntimeError, match="Publish failed"):
        publish_telemetry_event(test_event)

    rabbitmq_mocks["channel"].close.assert_called_once_with()
    rabbitmq_mocks["connection"].close.assert_called_once_with()


def test_publish_connection_failure(test_event, monkeypatch):
    with patch(
        "shared.rabbitmq_publisher.get_rabbitmq_connection",
        side_effect=RuntimeError("Connection failed"),
    ) as mock_get_connection:
        with pytest.raises(RuntimeError, match="Connection failed"):
            publish_telemetry_event(test_event)

    mock_get_connection.assert_called_once_with()


def test_publish_rejects_nan_value(test_event, rabbitmq_mocks):
    test_event["payload"]["value"] = float("nan")

    with pytest.raises(ValueError, match="Out of range float values"):
        publish_telemetry_event(test_event)

    rabbitmq_mocks["channel"].close.assert_called_once_with()
    rabbitmq_mocks["connection"].close.assert_called_once_with()
