
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class WorkspaceSettingsUpdate(BaseModel):
    workspace_name: str = Field(
        min_length=1,
        max_length=100,
    )
    description: str | None = Field(
        default=None,
        max_length=500,
    )
    environment: Literal[
        "development",
        "staging",
        "production",
    ] = "development"
    timezone: str = Field(
        default="Asia/Kolkata",
        min_length=1,
        max_length=100,
    )
    refresh_interval: int = Field(
        default=30,
        ge=15,
        le=300,
    )
    notification_preferences: dict | None = None


class WorkspaceSettingsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    workspace_name: str
    description: str | None
    environment: str
    timezone: str
    refresh_interval: int
    notification_preferences: dict | None
    created_at: datetime
    updated_at: datetime
