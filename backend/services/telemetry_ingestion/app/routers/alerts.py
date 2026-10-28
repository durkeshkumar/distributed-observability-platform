
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from shared.database import get_db
from services.telemetry_ingestion.app.models.alert import Alert

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("")
def list_alerts(
    status: Literal["firing", "acknowledged", "resolved"] | None = None,
    severity: Literal["info", "warning", "critical"] | None = None,
    service_name: str | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    """List alerts with optional filters and pagination."""

    query = db.query(Alert)

    if status:
        query = query.filter(Alert.status == status)

    if severity:
        query = query.filter(Alert.severity == severity)

    if service_name:
        query = query.filter(Alert.service_name == service_name)

    total = query.count()

    alerts = (
        query.order_by(Alert.created_at.desc(), Alert.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": [
            {
                "id": alert.id,
                "alert_key": alert.alert_key,
                "alert_name": alert.alert_name,
                "service_name": alert.service_name,
                "metric_name": alert.metric_name,
                "observed_value": alert.observed_value,
                "threshold_value": alert.threshold_value,
                "severity": alert.severity,
                "status": alert.status,
                "description": alert.description,
                "attributes": alert.attributes,
                "fired_at": alert.fired_at,
                "acknowledged_at": alert.acknowledged_at,
                "resolved_at": alert.resolved_at,
                "created_at": alert.created_at,
            }
            for alert in alerts
        ],
    }


@router.get("/{alert_id}")
def get_alert(
    alert_id: int,
    db: Session = Depends(get_db),
):
    """Retrieve a single alert by its database ID."""

    alert = db.query(Alert).filter(Alert.id == alert_id).first()

    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")

    return {
        "id": alert.id,
        "alert_key": alert.alert_key,
        "alert_name": alert.alert_name,
        "service_name": alert.service_name,
        "metric_name": alert.metric_name,
        "observed_value": alert.observed_value,
        "threshold_value": alert.threshold_value,
        "severity": alert.severity,
        "status": alert.status,
        "description": alert.description,
        "attributes": alert.attributes,
        "fired_at": alert.fired_at,
        "acknowledged_at": alert.acknowledged_at,
        "resolved_at": alert.resolved_at,
        "created_at": alert.created_at,
    }


@router.post("/{alert_id}/acknowledge")
def acknowledge_alert_endpoint(
    alert_id: int,
    db: Session = Depends(get_db),
):
    """Acknowledge an alert that is currently firing."""

    from services.telemetry_ingestion.app.services.alert_lifecycle_service import (
        acknowledge_alert,
    )

    alert = acknowledge_alert(db, alert_id)

    if alert is None:
        raise HTTPException(
            status_code=409,
            detail="Alert not found or is not in firing status",
        )

    return {
        "message": "Alert acknowledged",
        "id": alert.id,
        "status": alert.status,
        "acknowledged_at": alert.acknowledged_at,
    }


@router.post("/{alert_id}/resolve")
def resolve_alert_endpoint(
    alert_id: int,
    db: Session = Depends(get_db),
):
    """Resolve an active alert."""

    from services.telemetry_ingestion.app.services.alert_lifecycle_service import (
        resolve_alert,
    )

    alert = resolve_alert(db, alert_id)

    if alert is None:
        raise HTTPException(
            status_code=409,
            detail="Alert not found or is already resolved",
        )

    return {
        "message": "Alert resolved",
        "id": alert.id,
        "status": alert.status,
        "resolved_at": alert.resolved_at,
    }
