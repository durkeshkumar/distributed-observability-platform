
from datetime import datetime

from sqlalchemy.orm import Session

from services.telemetry_ingestion.app.models.alert import Alert


def create_or_update_alert(
    db: Session,
    *,
    alert_key: str,
    alert_name: str,
    service_name: str,
    metric_name: str,
    observed_value: float,
    threshold_value: float,
    severity: str = "warning",
    description: str | None = None,
    attributes: dict | None = None,
) -> Alert:
    """Create a new alert or update an existing active alert."""

    alert = (
        db.query(Alert)
        .filter(Alert.alert_key == alert_key)
        .first()
    )

    now = datetime.utcnow()

    if alert is not None:
        # Reuse an existing alert while it remains active.
        if alert.status in ("firing", "acknowledged"):
            alert.observed_value = observed_value
            alert.threshold_value = threshold_value
            alert.severity = severity
            alert.description = description
            alert.attributes = attributes
            db.commit()
            db.refresh(alert)
            return alert

        # Start a new alert lifecycle after a previous resolution.
        alert.alert_name = alert_name
        alert.service_name = service_name
        alert.metric_name = metric_name
        alert.observed_value = observed_value
        alert.threshold_value = threshold_value
        alert.severity = severity
        alert.status = "firing"
        alert.description = description
        alert.attributes = attributes
        alert.fired_at = now
        alert.acknowledged_at = None
        alert.resolved_at = None

        db.commit()
        db.refresh(alert)
        return alert

    alert = Alert(
        alert_key=alert_key,
        alert_name=alert_name,
        service_name=service_name,
        metric_name=metric_name,
        observed_value=observed_value,
        threshold_value=threshold_value,
        severity=severity,
        status="firing",
        description=description,
        attributes=attributes,
        fired_at=now,
    )

    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


def acknowledge_alert(db: Session, alert_id: int) -> Alert | None:
    """Acknowledge an alert that is currently firing."""

    alert = db.query(Alert).filter(Alert.id == alert_id).first()

    if alert is None or alert.status != "firing":
        return None

    alert.status = "acknowledged"
    alert.acknowledged_at = datetime.utcnow()

    db.commit()
    db.refresh(alert)
    return alert


def resolve_alert(db: Session, alert_id: int) -> Alert | None:
    """Resolve an alert that is currently active."""

    alert = db.query(Alert).filter(Alert.id == alert_id).first()

    if alert is None or alert.status not in ("firing", "acknowledged"):
        return None

    alert.status = "resolved"
    alert.resolved_at = datetime.utcnow()

    db.commit()
    db.refresh(alert)
    return alert
