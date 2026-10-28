
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class MetricRecordResponse(BaseModel):
    """Response schema for a stored metric record."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    event_id: str
    service_name: str
    metric_name: str
    metric_type: str
    value: float
    unit: str | None = None
    timestamp: datetime
    attributes: dict[str, Any] | None = None
    created_at: datetime


class MetricListResponse(BaseModel):
    """Paginated metric query response."""

    total: int
    limit: int
    offset: int
    items: list[MetricRecordResponse]
