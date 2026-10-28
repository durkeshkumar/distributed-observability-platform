
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TraceSpanResponse(BaseModel):
    id: int
    trace_id: str
    span_id: str
    parent_span_id: str | None
    service_name: str
    operation_name: str
    start_time: datetime
    end_time: datetime | None
    duration_ms: float | None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
