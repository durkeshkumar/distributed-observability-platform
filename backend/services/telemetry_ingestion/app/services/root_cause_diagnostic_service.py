from collections import defaultdict
from typing import Any


SLOW_SPAN_THRESHOLD_MS = 500.0

METRIC_RULES = {
    "cpu_usage_percent": {
        "threshold": 80.0,
        "operator": ">=",
        "score": 3,
    },
    "error_rate_percent": {
        "threshold": 5.0,
        "operator": ">",
        "score": 4,
    },
    "request_latency_ms": {
        "threshold": 500.0,
        "operator": ">",
        "score": 3,
    },
}


def analyze_root_cause(
    correlation_data: dict[str, Any],
) -> dict[str, Any]:
    """
    Analyze correlated spans, logs, and metrics.

    Returns ranked service-level diagnostic findings.
    This is heuristic evidence, not a confirmed causal diagnosis.
    """

    trace_id = correlation_data.get("trace_id")

    findings = defaultdict(
        lambda: {
            "score": 0,
            "issues": [],
        }
    )

    # Rule 1: Failed spans
    for span in correlation_data.get("spans", []):
        service = span["service_name"]
        status = str(span.get("status") or "").upper()

        if status in {"ERROR", "FAILED"}:
            findings[service]["score"] += 5
            findings[service]["issues"].append(
                {
                    "type": "FAILED_SPAN",
                    "score": 5,
                    "message": (
                        f"Operation '{span['operation_name']}' "
                        f"reported status {status}"
                    ),
                    "span_id": span["span_id"],
                }
            )

        # Rule 2: Slow spans
        duration = span.get("duration_ms")

        if duration is not None and duration > SLOW_SPAN_THRESHOLD_MS:
            findings[service]["score"] += 3
            findings[service]["issues"].append(
                {
                    "type": "SLOW_SPAN",
                    "score": 3,
                    "message": (
                        f"Operation '{span['operation_name']}' "
                        f"took {duration:.2f} ms"
                    ),
                    "span_id": span["span_id"],
                }
            )

    # Rule 3: Error and critical logs
    for log in correlation_data.get("logs", []):
        service = log["service_name"]
        severity = str(log.get("severity") or "").upper()

        if severity == "CRITICAL":
            score = 5
        elif severity == "ERROR":
            score = 4
        else:
            continue

        findings[service]["score"] += score
        findings[service]["issues"].append(
            {
                "type": "ERROR_LOG",
                "score": score,
                "severity": severity,
                "message": log["message"],
                "log_id": log["id"],
            }
        )

    # Rule 4: Metric threshold violations
    for metric in correlation_data.get("metrics", []):
        metric_name = metric.get("metric_name")
        rule = METRIC_RULES.get(metric_name)

        if rule is None:
            continue

        value = metric.get("value")

        if value is None:
            continue

        try:
            value = float(value)
        except (TypeError, ValueError):
            continue

        from math import isfinite

        if not isfinite(value):
            continue

        threshold = rule["threshold"]

        if rule["operator"] == ">=":
            violated = value >= threshold
        else:
            violated = value > threshold

        if not violated:
            continue

        service = metric["service_name"]
        score = rule["score"]

        findings[service]["score"] += score
        findings[service]["issues"].append(
            {
                "type": "METRIC_ANOMALY",
                "score": score,
                "metric_name": metric_name,
                "observed_value": value,
                "threshold": threshold,
                "message": (
                    f"{metric_name} is {value}, "
                    f"threshold {rule['operator']} {threshold}"
                ),
            }
        )

    ranked_services = [
        {
            "service_name": service,
            "score": data["score"],
            "issue_count": len(data["issues"]),
            "issues": data["issues"],
        }
        for service, data in findings.items()
    ]

    ranked_services.sort(
        key=lambda item: (-item["score"], item["service_name"])
    )

    most_suspected_service = (
        ranked_services[0]["service_name"]
        if ranked_services
        else None
    )

    return {
        "trace_id": trace_id,
        "most_suspected_service": most_suspected_service,
        "total_issues": sum(
            item["issue_count"] for item in ranked_services
        ),
        "ranked_services": ranked_services,
        "analysis_status": (
            "POTENTIAL_ISSUES_FOUND"
            if ranked_services
            else "NO_ISSUES_DETECTED"
        ),
    }