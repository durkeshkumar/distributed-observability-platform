
from datetime import datetime, timezone
import math
from typing import Any, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


EventType = Literal["log", "trace", "metric"]
SeverityLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class IngestionEventCreate(BaseModel):
    event_id: str = Field(min_length=1, max_length=100)
    event_type: EventType
    service_name: str = Field(min_length=1, max_length=100)

    trace_id: str | None = Field(default=None, max_length=100)
    event_timestamp: datetime | None = None
    severity: SeverityLevel | None = None
    payload: dict[str, Any] | None = None

    processing_status: str = Field(default="received", max_length=30)
    error_message: str | None = None

    @field_validator("event_id", "service_name")
    @classmethod
    def strip_required_strings(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Value must not be empty or whitespace")
        return value

    @field_validator("trace_id")
    @classmethod
    def validate_trace_id(cls, value: str | None) -> str | None:
        if value is not None:
            value = value.strip()
            if not value:
                raise ValueError("trace_id must not be empty")
        return value

    @field_validator("severity", mode="before")
    @classmethod
    def normalize_severity(cls, value: Any) -> Any:
        if isinstance(value, str):
            return value.strip().upper()
        return value

    @field_validator("event_timestamp")
    @classmethod
    def normalize_timestamp(
        cls,
        value: datetime | None,
    ) -> datetime | None:
        if value is None:
            return None

        # Interpret timestamps without an offset as UTC.
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)

        # Convert timezone-aware values to UTC.
        return value.astimezone(timezone.utc).replace(tzinfo=None)

    @model_validator(mode="after")
    def validate_type_specific_payload(self):
        if not isinstance(self.payload, dict):
            raise ValueError(
                f"{self.event_type} events require a JSON payload object"
            )

        if self.event_type == "log":
            message = self.payload.get("message")
            if not isinstance(message, str) or not message.strip():
                raise ValueError(
                    "Log events require a non-empty payload.message"
                )

        elif self.event_type == "trace":
            if not self.trace_id:
                raise ValueError(
                    "Trace events require a non-empty trace_id"
                )

            operation = self.payload.get("operation")
            if not isinstance(operation, str) or not operation.strip():
                raise ValueError(
                    "Trace events require a non-empty payload.operation"
                )

        elif self.event_type == "metric":
            metric_name = self.payload.get("metric_name")
            value = self.payload.get("value")

            if not isinstance(metric_name, str) or not metric_name.strip():
                raise ValueError(
                    "Metric events require a non-empty payload.metric_name"
                )

            # Reject booleans, non-numeric values, NaN and infinity.
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
            ):
                raise ValueError(
                    "Metric events require a finite numeric payload.value"
                )

        return self


class IngestionEventResponse(BaseModel):
    id: int
    event_id: str
    event_type: str
    service_name: str
    trace_id: str | None
    event_timestamp: datetime | None
    severity: str | None
    payload: dict[str, Any] | None
    received_at: datetime
    processing_status: str
    error_message: str | None

    model_config = ConfigDict(from_attributes=True)


class BatchIngestionRequest(BaseModel):
    events: list[Any] = Field(min_length=1, max_length=100)


class BatchEventResult(BaseModel):
    event_id: str | None = None
    status: Literal["accepted", "duplicate", "rejected"]
    message: str


class BatchIngestionResponse(BaseModel):
    total: int
    accepted: int
    duplicates: int
    rejected: int
    results: list[BatchEventResult]
