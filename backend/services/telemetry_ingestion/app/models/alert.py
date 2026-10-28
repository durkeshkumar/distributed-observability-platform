
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Index, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from shared.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    __table_args__ = (
        Index("ix_alerts_service_name", "service_name"),
        Index("ix_alerts_severity", "severity"),
        Index("ix_alerts_status", "status"),
        Index("ix_alerts_created_at", "created_at"),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    alert_key: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        nullable=False,
        index=True,
    )

    alert_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    service_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    metric_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    observed_value: Mapped[float] = mapped_column(
        nullable=False,
    )

    threshold_value: Mapped[float] = mapped_column(
        nullable=False,
    )

    severity: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="warning",
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="firing",
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    attributes: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )

    fired_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    acknowledged_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )
