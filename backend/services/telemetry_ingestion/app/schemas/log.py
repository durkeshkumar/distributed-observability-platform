
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class LogRecordResponse(BaseModel):
    """Response schema for a single stored log record."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    event_id: str
    service_name: str
    message: str
    severity: str
    timestamp: datetime
    trace_id: str | None = None
    attributes: dict[str, Any] | None = None
    created_at: datetime


class LogListResponse(BaseModel):
    """Paginated response for log searches."""

    total: int
    limit: int
    offset: int
    items: list[LogRecordResponse]
