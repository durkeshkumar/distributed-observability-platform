
import logging
from typing import Any

logger = logging.getLogger(__name__)


def send_alert_notification(alert: Any) -> dict:
    """
    Log a notification for an alert.

    This is a local logging-based notification service.
    It does not send emails or external messages.
    """

    notification = {
        "alert_id": alert.id,
        "alert_key": alert.alert_key,
        "alert_name": alert.alert_name,
        "service_name": alert.service_name,
        "metric_name": alert.metric_name,
        "observed_value": alert.observed_value,
        "threshold_value": alert.threshold_value,
        "severity": alert.severity,
        "status": alert.status,
        "message": (
            f"[{alert.severity.upper()}] {alert.alert_name}: "
            f"{alert.service_name} metric '{alert.metric_name}' "
            f"has value {alert.observed_value}; "
            f"threshold is {alert.threshold_value}."
        ),
    }

    logger.warning(
        "ALERT NOTIFICATION: %s",
        notification["message"],
        extra={
            "alert_id": alert.id,
            "alert_key": alert.alert_key,
            "alert_severity": alert.severity,
        },
    )

    return notification
