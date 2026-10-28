
import os

import pika
from dotenv import load_dotenv

load_dotenv()


def get_rabbitmq_connection() -> pika.BlockingConnection:
    """Create a new connection to the RabbitMQ broker."""
    host = os.getenv("RABBITMQ_HOST", "localhost")
    port = int(os.getenv("RABBITMQ_PORT", "5672"))
    username = os.getenv("RABBITMQ_USER")
    password = os.getenv("RABBITMQ_PASSWORD")

    if not username or not password:
        raise RuntimeError(
            "RABBITMQ_USER and RABBITMQ_PASSWORD must be set in .env"
        )

    credentials = pika.PlainCredentials(username, password)

    parameters = pika.ConnectionParameters(
        host=host,
        port=port,
        credentials=credentials,
        heartbeat=60,
        blocked_connection_timeout=30,
        socket_timeout=10,
        connection_attempts=3,
        retry_delay=2,
    )

    return pika.BlockingConnection(parameters)


def declare_telemetry_queue(
    connection: pika.BlockingConnection,
) -> None:
    """Declare the durable queue used for telemetry events."""
    queue_name = os.getenv(
        "RABBITMQ_QUEUE",
        "telemetry_events",
    )

    channel = connection.channel()

    try:
        channel.queue_declare(
            queue=queue_name,
            durable=True,
        )
    finally:
        channel.close()
