
from datetime import datetime
from typing import Any

from sqlalchemy import (
    DateTime,
    Index,
    Integer,
    JSON,
    String,
    func,
)
from sqlalchemy.dialects.mysql import DOUBLE
from sqlalchemy.orm import Mapped, mapped_column

from shared.database import Base


class MetricRecord(Base):
    __tablename__ = "metric_records"

    __table_args__ = (
        Index("ix_metric_records_service_name", "service_name"),
        Index("ix_metric_records_metric_name", "metric_name"),
        Index("ix_metric_records_timestamp", "timestamp"),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    event_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    service_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    metric_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    metric_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    value: Mapped[float] = mapped_column(
        DOUBLE,
        nullable=False,
    )

    unit: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    attributes: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )
