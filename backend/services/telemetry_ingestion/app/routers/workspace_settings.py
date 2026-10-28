
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from shared.database import get_db
from services.telemetry_ingestion.app.models.workspace_settings import (
    WorkspaceSettings,
)
from services.telemetry_ingestion.app.schemas.workspace_settings import (
    WorkspaceSettingsUpdate,
    WorkspaceSettingsResponse,
)

router = APIRouter(
    prefix="/settings",
    tags=["Workspace Settings"],
)


def get_or_create_settings(db: Session) -> WorkspaceSettings:
    settings = (
        db.query(WorkspaceSettings)
        .order_by(WorkspaceSettings.id.asc())
        .first()
    )

    if settings is None:
        settings = WorkspaceSettings(
            workspace_name="Observability Workspace",
            description="Monitor services, telemetry, and application health.",
            environment="development",
            timezone="Asia/Kolkata",
            refresh_interval=30,
            notification_preferences={},
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)

    return settings


@router.get("", response_model=WorkspaceSettingsResponse)
def read_workspace_settings(
    db: Session = Depends(get_db),
):
    return get_or_create_settings(db)


@router.put("", response_model=WorkspaceSettingsResponse)
def update_workspace_settings(
    payload: WorkspaceSettingsUpdate,
    db: Session = Depends(get_db),
):
    settings = get_or_create_settings(db)

    settings.workspace_name = payload.workspace_name
    settings.description = payload.description
    settings.environment = payload.environment
    settings.timezone = payload.timezone
    settings.refresh_interval = payload.refresh_interval
    settings.notification_preferences = payload.notification_preferences

    try:
        db.commit()
        db.refresh(settings)
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to save workspace settings.",
        ) from exc

    return settings
