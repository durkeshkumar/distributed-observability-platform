
from math import isfinite

from services.telemetry_ingestion.app.services.alert_rule_service import (
    AlertRule,
    evaluate_alert_rule,
    get_default_alert_rules,
)


def evaluate_metric_against_rules(
    service_name: str,
    metric_name: str,
    observed_value: float,
    rules: list[AlertRule] | None = None,
) -> list[dict]:
    """
    Evaluate a metric against applicable alert rules.

    A rule applies when its metric matches and its service name
    matches the incoming service or is '*'.
    """

    if isinstance(observed_value, bool) or not isinstance(
        observed_value, (int, float)
    ):
        raise ValueError("Observed metric value must be numeric.")

    if not isfinite(observed_value):
        raise ValueError("Observed metric value must be finite.")

    configured_rules = (
        rules if rules is not None else get_default_alert_rules()
    )

    triggered_alerts = []

    for rule in configured_rules:
        service_matches = (
            rule.service_name == "*"
            or rule.service_name == service_name
        )

        if not service_matches or rule.metric_name != metric_name:
            continue

        result = evaluate_alert_rule(rule, observed_value)

        if result["triggered"]:
            triggered_alerts.append(result)

    return triggered_alerts
