
from collections import defaultdict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from shared.database import get_db
from services.telemetry_ingestion.app.models import TraceSpan

router = APIRouter(prefix="/service-map", tags=["Service Map"])


@router.get("")
def get_service_map(db: Session = Depends(get_db)):
    """
    Build a service dependency map from stored trace spans.

    A directed dependency is created only when a child span references
    a parent span in the same trace and the two spans belong to
    different services.
    """
    spans = db.query(TraceSpan).order_by(TraceSpan.id.asc()).all()

    service_stats = defaultdict(
        lambda: {
            "span_count": 0,
            "duration_total_ms": 0.0,
            "duration_count": 0,
            "error_count": 0,
        }
    )

    # Index spans by (trace_id, span_id) to avoid linking spans
    # belonging to different traces.
    span_index = {
        (span.trace_id, span.span_id): span
        for span in spans
    }

    # Count real spans and aggregate service statistics.
    for span in spans:
        stats = service_stats[span.service_name]
        stats["span_count"] += 1

        if span.duration_ms is not None:
            stats["duration_total_ms"] += float(span.duration_ms)
            stats["duration_count"] += 1

        if span.status.upper() in {"ERROR", "FAILED"}:
            stats["error_count"] += 1

    # Count observed cross-service parent-child relationships.
    edge_counts = defaultdict(int)

    for child in spans:
        if not child.parent_span_id:
            continue

        parent = span_index.get(
            (child.trace_id, child.parent_span_id)
        )

        if parent is None:
            continue

        if parent.service_name == child.service_name:
            continue

        edge_counts[
            (parent.service_name, child.service_name)
        ] += 1

    nodes = []

    for service_name in sorted(service_stats):
        stats = service_stats[service_name]
        duration_count = stats["duration_count"]

        avg_duration = (
            round(stats["duration_total_ms"] / duration_count, 2)
            if duration_count
            else None
        )

        nodes.append(
            {
                "id": service_name,
                "name": service_name,
                "span_count": stats["span_count"],
                "avg_duration_ms": avg_duration,
                "error_count": stats["error_count"],
            }
        )

    edges = [
        {
            "source": source,
            "target": target,
            "calls": calls,
        }
        for (source, target), calls in sorted(edge_counts.items())
    ]

    return {
        "nodes": nodes,
        "edges": edges,
        "summary": {
            "service_count": len(nodes),
            "dependency_count": len(edges),
            "span_count": len(spans),
        },
    }
