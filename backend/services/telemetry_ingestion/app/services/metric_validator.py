
import math
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


SUPPORTED_METRIC_TYPES = {
    "counter",
    "gauge",
    "histogram",
}


class MetricEvent(BaseModel):
    """Validated structure for an incoming metric event."""

    model_config = ConfigDict(extra="forbid")

    event_id: str = Field(min_length=1, max_length=100)
    service_name: str = Field(min_length=1, max_length=100)
    metric_name: str = Field(min_length=1, max_length=150)
    metric_type: str
    value: float
    unit: str | None = Field(default=None, max_length=30)
    timestamp: datetime
    attributes: dict[str, Any] | None = None

    @field_validator(
        "event_id",
        "service_name",
        "metric_name",
        "metric_type",
    )
    @classmethod
    def validate_non_empty_strings(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Field must not be empty")

        return value

    @field_validator("metric_type")
    @classmethod
    def validate_metric_type(cls, value: str) -> str:
        value = value.lower()

        if value not in SUPPORTED_METRIC_TYPES:
            raise ValueError(
                "metric_type must be counter, gauge, or histogram"
            )

        return value

    @field_validator("value")
    @classmethod
    def validate_finite_value(cls, value: float) -> float:
        if not math.isfinite(value):
            raise ValueError("Metric value must be a finite number")

        return value

    @field_validator("unit")
    @classmethod
    def validate_unit(cls, value: str | None) -> str | None:
        if value is not None:
            value = value.strip()

            if not value:
                return None

        return value
