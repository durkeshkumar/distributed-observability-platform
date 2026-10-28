
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Float,
    Index,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from shared.database import Base


class TraceSpan(Base):
    __tablename__ = "trace_spans"

    __table_args__ = (
        Index("ix_trace_spans_trace_id", "trace_id"),
        Index("ix_trace_spans_parent_span_id", "parent_span_id"),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    trace_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    span_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    parent_span_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    service_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    operation_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    start_time: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    end_time: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    duration_ms: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="UNSET",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )
