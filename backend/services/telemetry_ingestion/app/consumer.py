
import json
import logging
import os
import signal
import threading
from typing import Any

import pika
from sqlalchemy.exc import IntegrityError

from shared.database import SessionLocal
from shared.rabbitmq import (
    declare_telemetry_queue,
    get_rabbitmq_connection,
)
from services.telemetry_ingestion.app.services.log_processor import (
    process_log_event,
)
from services.telemetry_ingestion.app.services.trace_processor import (
    process_trace_event,
)
from services.telemetry_ingestion.app.services.metric_processor import (
    process_metric_event,
)
from services.telemetry_ingestion.app.services.alert_processing_service import (
    process_metric_for_alerts,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("telemetry_consumer")
shutdown_event = threading.Event()


def process_telemetry_event(event: dict[str, Any]) -> None:
    """Validate and process telemetry events from RabbitMQ."""

    event_id = event.get("event_id")
    event_type = event.get("event_type")
    service_name = event.get("service_name")

    if not isinstance(event_id, str) or not event_id.strip():
        raise ValueError("Message is missing a valid event_id")

    if event_type not in {"log", "trace", "metric"}:
        raise ValueError(f"Unsupported event_type: {event_type!r}")

    if not isinstance(service_name, str) or not service_name.strip():
        raise ValueError("Message is missing a valid service_name")

    if not isinstance(event.get("payload"), dict):
        raise ValueError("Message payload must be a JSON object")

    db = SessionLocal()

    try:
        if event_type == "log":
            record = process_log_event(db, event)

            logger.info(
                "Log record stored | event_id=%s | service=%s | severity=%s",
                record.event_id,
                record.service_name,
                record.severity,
            )

        elif event_type == "trace":
            span = process_trace_event(db, event)

            logger.info(
                "Trace span stored | event_id=%s | trace_id=%s "
                "| span_id=%s | duration_ms=%s",
                event_id,
                span.trace_id,
                span.span_id,
                span.duration_ms,
            )

        elif event_type == "metric":
            record = process_metric_event(db, event["payload"])

            logger.info(
                "Metric record stored | event_id=%s | metric=%s "
                "| value=%s | service=%s",
                record.event_id,
                record.metric_name,
                record.value,
                record.service_name,
            )

            triggered_alerts = process_metric_for_alerts(
                db,
                service_name=record.service_name,
                metric_name=record.metric_name,
                observed_value=record.value,
                attributes=record.attributes,
            )

            if triggered_alerts:
                logger.warning(
                    "Metric triggered %s alert(s) | event_id=%s | service=%s",
                    len(triggered_alerts),
                    record.event_id,
                    record.service_name,
                )

                for alert in triggered_alerts:
                    logger.warning(
                        "Alert processed | alert_id=%s | name=%s "
                        "| severity=%s | status=%s",
                        alert["alert_id"],
                        alert["alert_name"],
                        alert["severity"],
                        alert["status"],
                    )

    except IntegrityError:
        logger.exception(
            "Database integrity error processing event_id=%s",
            event_id,
        )
        raise

    finally:
        db.close()


def on_message(
    channel: pika.adapters.blocking_connection.BlockingChannel,
    method: pika.spec.Basic.Deliver,
    properties: pika.BasicProperties,
    body: bytes,
) -> None:
    """Decode, process, and acknowledge one RabbitMQ message."""

    try:
        event = json.loads(body.decode("utf-8"))

        if not isinstance(event, dict):
            raise ValueError("Message body must be a JSON object")

        process_telemetry_event(event)

    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        logger.error("Rejecting invalid telemetry message: %s", exc)
        channel.basic_reject(
            delivery_tag=method.delivery_tag,
            requeue=False,
        )
        return

    except Exception:
        logger.exception("Telemetry processing failed; requeueing message")
        channel.basic_nack(
            delivery_tag=method.delivery_tag,
            requeue=True,
        )
        return

    channel.basic_ack(delivery_tag=method.delivery_tag)


def request_shutdown(signum, frame) -> None:
    logger.info("Shutdown signal received")
    shutdown_event.set()


def main() -> None:
    signal.signal(signal.SIGINT, request_shutdown)
    signal.signal(signal.SIGTERM, request_shutdown)

    connection = None
    channel = None

    try:
        connection = get_rabbitmq_connection()
        declare_telemetry_queue(connection)

        channel = connection.channel()
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(
            queue=os.getenv("RABBITMQ_QUEUE", "telemetry_events"),
            on_message_callback=on_message,
            auto_ack=False,
        )

        logger.info("Telemetry consumer started")
        logger.info(
            "Waiting for messages from %s",
            os.getenv("RABBITMQ_QUEUE", "telemetry_events"),
        )

        while not shutdown_event.is_set():
            connection.process_data_events(time_limit=1)

    except KeyboardInterrupt:
        logger.info("Consumer interrupted")

    finally:
        if channel is not None and channel.is_open:
            try:
                channel.stop_consuming()
            except Exception:
                logger.exception("Error stopping consumer")

        if connection is not None and connection.is_open:
            connection.close()

        logger.info("Telemetry consumer stopped")


if __name__ == "__main__":
    main()
