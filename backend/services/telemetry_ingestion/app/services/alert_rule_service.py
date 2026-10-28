
from dataclasses import dataclass
from math import isfinite
from typing import Literal


ComparisonOperator = Literal[">", ">=", "<", "<=", "=="]


@dataclass(frozen=True)
class AlertRule:
    rule_name: str
    service_name: str
    metric_name: str
    threshold_value: float
    comparison_operator: ComparisonOperator = ">"
    severity: str = "warning"
    description: str = ""


DEFAULT_ALERT_RULES = [
    AlertRule(
        rule_name="High API Latency",
        service_name="api-gateway",
        metric_name="request_latency_ms",
        threshold_value=500.0,
        comparison_operator=">",
        severity="warning",
        description="API request latency has exceeded 500 ms.",
    ),
    AlertRule(
        rule_name="High Error Rate",
        service_name="api-gateway",
        metric_name="error_rate_percent",
        threshold_value=5.0,
        comparison_operator=">",
        severity="critical",
        description="API error rate has exceeded 5%.",
    ),
    AlertRule(
        rule_name="High CPU Usage",
        service_name="*",
        metric_name="cpu_usage_percent",
        threshold_value=80.0,
        comparison_operator=">=",
        severity="warning",
        description="CPU usage has reached or exceeded 80%.",
    ),
]


def evaluate_alert_rule(
    rule: AlertRule,
    observed_value: float,
) -> dict:
    """Evaluate one metric value against an alert rule."""

    if isinstance(observed_value, bool) or not isinstance(
        observed_value, (int, float)
    ):
        raise ValueError("Observed value must be numeric.")

    if not isfinite(observed_value):
        raise ValueError("Observed value must be finite.")

    if not isfinite(rule.threshold_value):
        raise ValueError("Threshold value must be finite.")

    operators = {
        ">": lambda value, threshold: value > threshold,
        ">=": lambda value, threshold: value >= threshold,
        "<": lambda value, threshold: value < threshold,
        "<=": lambda value, threshold: value <= threshold,
        "==": lambda value, threshold: value == threshold,
    }

    triggered = operators[rule.comparison_operator](
        observed_value,
        rule.threshold_value,
    )

    return {
        "rule_name": rule.rule_name,
        "service_name": rule.service_name,
        "metric_name": rule.metric_name,
        "observed_value": observed_value,
        "threshold_value": rule.threshold_value,
        "comparison_operator": rule.comparison_operator,
        "severity": rule.severity,
        "triggered": triggered,
        "description": rule.description,
    }


def get_default_alert_rules() -> list[AlertRule]:
    """Return the configured default alert rules."""
    return list(DEFAULT_ALERT_RULES)
