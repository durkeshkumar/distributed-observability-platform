
from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class MetricThreshold:
    """Configuration for a metric threshold."""

    metric_name: str
    limit: float
    comparison: Literal["gt", "gte", "lt", "lte"] = "gt"
    service_name: str | None = None


def evaluate_threshold(
    threshold: MetricThreshold,
    value: float,
) -> dict:
    """Evaluate a metric value against a configured threshold."""

    comparisons = {
        "gt": value > threshold.limit,
        "gte": value >= threshold.limit,
        "lt": value < threshold.limit,
        "lte": value <= threshold.limit,
    }

    return {
        "metric_name": threshold.metric_name,
        "service_name": threshold.service_name,
        "value": value,
        "threshold": threshold.limit,
        "comparison": threshold.comparison,
        "exceeded": comparisons[threshold.comparison],
    }


def evaluate_error_rate(
    error_rate: float | None,
    threshold_percent: float = 5.0,
    service_name: str | None = None,
) -> dict:
    """Check whether an error rate exceeds a percentage threshold."""

    if error_rate is None:
        return {
            "metric_name": "error_rate",
            "service_name": service_name,
            "value": None,
            "threshold": threshold_percent,
            "comparison": "gt",
            "exceeded": False,
            "status": "insufficient_data",
        }

    result = evaluate_threshold(
        MetricThreshold(
            metric_name="error_rate",
            limit=threshold_percent,
            comparison="gt",
            service_name=service_name,
        ),
        error_rate,
    )

    result["status"] = (
        "threshold_exceeded" if result["exceeded"] else "normal"
    )

    return result
