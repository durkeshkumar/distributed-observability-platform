
from datetime import datetime

from sqlalchemy import DateTime, Integer, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column

from shared.database import Base


class WorkspaceSettings(Base):
    __tablename__ = "workspace_settings"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    workspace_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="Observability Workspace",
    )

    description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    environment: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="development",
    )

    timezone: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="Asia/Kolkata",
    )

    refresh_interval: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=30,
    )

    notification_preferences: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
