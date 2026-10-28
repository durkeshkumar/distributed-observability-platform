
import json
import os
from typing import Any

import pika

from shared.rabbitmq import (
    declare_telemetry_queue,
    get_rabbitmq_connection,
)


def publish_telemetry_event(event: dict[str, Any]) -> bool:
    """
    Publish a telemetry event to RabbitMQ.

    The message is persistent, and publisher confirms are enabled.
    Raises an exception if publishing fails.
    """
    queue_name = os.getenv(
        "RABBITMQ_QUEUE",
        "telemetry_events",
    )

    event_id = event.get("event_id")
    if not isinstance(event_id, str) or not event_id.strip():
        raise ValueError("Telemetry event must have a valid event_id")

    connection = None
    channel = None

    try:
        connection = get_rabbitmq_connection()
        declare_telemetry_queue(connection)

        channel = connection.channel()
        channel.confirm_delivery()

        message_body = json.dumps(
            event,
            ensure_ascii=False,
            allow_nan=False,
        )

        properties = pika.BasicProperties(
            content_type="application/json",
            delivery_mode=2,
            message_id=event_id,
        )

        confirmed = channel.basic_publish(
            exchange="",
            routing_key=queue_name,
            body=message_body.encode("utf-8"),
            properties=properties,
            mandatory=True,
        )

        if confirmed is False:
            raise RuntimeError(
                f"RabbitMQ did not confirm event {event_id}"
            )

        return True

    finally:
        if channel is not None and channel.is_open:
            channel.close()

        if connection is not None and connection.is_open:
            connection.close()
