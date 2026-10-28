
import pytest
from unittest.mock import MagicMock, patch

from shared.rabbitmq import (
    declare_telemetry_queue,
    get_rabbitmq_connection,
)


@patch("shared.rabbitmq.pika.BlockingConnection")
@patch("shared.rabbitmq.pika.ConnectionParameters")
@patch("shared.rabbitmq.pika.PlainCredentials")
def test_get_rabbitmq_connection_success(
    mock_credentials,
    mock_parameters,
    mock_blocking_connection,
    monkeypatch,
):
    monkeypatch.setenv("RABBITMQ_HOST", "localhost")
    monkeypatch.setenv("RABBITMQ_PORT", "5672")
    monkeypatch.setenv("RABBITMQ_USER", "test-user")
    monkeypatch.setenv("RABBITMQ_PASSWORD", "test-password")

    expected_connection = MagicMock()
    mock_blocking_connection.return_value = expected_connection

    result = get_rabbitmq_connection()

    mock_credentials.assert_called_once_with("test-user", "test-password")
    mock_parameters.assert_called_once()
    mock_blocking_connection.assert_called_once_with(
        mock_parameters.return_value
    )
    assert result is expected_connection


@pytest.mark.parametrize(
    ("username", "password"),
    [
        ("", "test-password"),
        ("test-user", ""),
        (None, None),
    ],
)
def test_get_rabbitmq_connection_missing_credentials(
    monkeypatch, username, password
):
    if username is None:
        monkeypatch.delenv("RABBITMQ_USER", raising=False)
    else:
        monkeypatch.setenv("RABBITMQ_USER", username)

    if password is None:
        monkeypatch.delenv("RABBITMQ_PASSWORD", raising=False)
    else:
        monkeypatch.setenv("RABBITMQ_PASSWORD", password)

    with pytest.raises(
        RuntimeError,
        match="RABBITMQ_USER and RABBITMQ_PASSWORD must be set",
    ):
        get_rabbitmq_connection()


def test_declare_telemetry_queue_uses_durable_queue(monkeypatch):
    monkeypatch.setenv("RABBITMQ_QUEUE", "test_telemetry_events")

    connection = MagicMock()
    channel = connection.channel.return_value
    channel.is_open = True

    declare_telemetry_queue(connection)

    connection.channel.assert_called_once_with()
    channel.queue_declare.assert_called_once_with(
        queue="test_telemetry_events",
        durable=True,
    )
    channel.close.assert_called_once_with()


def test_declare_telemetry_queue_closes_channel_on_error():
    connection = MagicMock()
    channel = connection.channel.return_value
    channel.queue_declare.side_effect = RuntimeError("Queue declaration failed")

    with pytest.raises(RuntimeError, match="Queue declaration failed"):
        declare_telemetry_queue(connection)

    channel.close.assert_called_once_with()
