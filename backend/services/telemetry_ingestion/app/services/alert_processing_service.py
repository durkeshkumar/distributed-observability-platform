
import logging
from math import isfinite

from sqlalchemy.orm import Session

from services.telemetry_ingestion.app.services.alert_evaluation_service import (
    evaluate_metric_against_rules,
)
from services.telemetry_ingestion.app.services.alert_lifecycle_service import (
    create_or_update_alert,
)
from services.telemetry_ingestion.app.services.alert_notification_service import (
    send_alert_notification,
)

logger = logging.getLogger(__name__)


def process_metric_for_alerts(
    db: Session,
    *,
    service_name: str,
    metric_name: str,
    observed_value: float,
    attributes: dict | None = None,
) -> list[dict]:
    """Evaluate metrics, persist triggered alerts, and notify on new alerts."""

    if isinstance(observed_value, bool) or not isinstance(
        observed_value, (int, float)
    ):
        raise ValueError("Observed metric value must be numeric.")

    if not isfinite(observed_value):
        raise ValueError("Observed metric value must be finite.")

    triggered_rules = evaluate_metric_against_rules(
        service_name=service_name,
        metric_name=metric_name,
        observed_value=observed_value,
    )

    processed_alerts = []

    for rule_result in triggered_rules:
        alert_key = f"{service_name}:{rule_result['rule_name']}"

        existing_alert = (
            db.query(
                __import__(
                    "services.telemetry_ingestion.app.models.alert",
                    fromlist=["Alert"],
                ).Alert
            )
            .filter_by(alert_key=alert_key)
            .first()
        )

        should_notify = (
            existing_alert is None
            or existing_alert.status == "resolved"
        )

        alert = create_or_update_alert(
            db,
            alert_key=alert_key,
            alert_name=rule_result["rule_name"],
            service_name=service_name,
            metric_name=metric_name,
            observed_value=observed_value,
            threshold_value=rule_result["threshold_value"],
            severity=rule_result["severity"],
            description=rule_result["description"],
            attributes=attributes,
        )

        notification = None
        if should_notify:
            notification = send_alert_notification(alert)

        processed_alerts.append(
            {
                "alert_id": alert.id,
                "alert_key": alert.alert_key,
                "alert_name": alert.alert_name,
                "service_name": alert.service_name,
                "metric_name": alert.metric_name,
                "observed_value": alert.observed_value,
                "threshold_value": alert.threshold_value,
                "severity": alert.severity,
                "status": alert.status,
                "notification": notification,
            }
        )

    return processed_alerts
