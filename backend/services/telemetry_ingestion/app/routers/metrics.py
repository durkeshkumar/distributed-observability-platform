
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session

from shared.database import get_db
from services.telemetry_ingestion.app.models import MetricRecord
from services.telemetry_ingestion.app.schemas.metric import (
    MetricListResponse,
    MetricRecordResponse,
)
from services.telemetry_ingestion.app.services.metric_query_service import (
    get_metric_by_id,
    list_metrics,
)
from services.telemetry_ingestion.app.services.metric_aggregation_service import (
    get_request_count,
    get_error_rate,
    get_average_latency,
    group_metrics_by_service,
)

router = APIRouter(prefix="/metrics", tags=["Metrics"])


@router.get("", response_model=MetricListResponse)
def get_metrics(
    service_name: str | None = Query(default=None, min_length=1),
    metric_name: str | None = Query(default=None, min_length=1),
    metric_type: str | None = Query(default=None, min_length=1),
    start_time: datetime | None = Query(default=None),
    end_time: datetime | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    """List stored metrics with optional filters and pagination."""

    if start_time and end_time and start_time > end_time:
        raise HTTPException(
            status_code=422,
            detail="start_time must be earlier than or equal to end_time",
        )

    total, items = list_metrics(
        db,
        service_name=service_name,
        metric_name=metric_name,
        metric_type=metric_type,
        start_time=start_time,
        end_time=end_time,
        limit=limit,
        offset=offset,
    )

    return MetricListResponse(
        total=total,
        limit=limit,
        offset=offset,
        items=items,
    )


@router.get("/summary/request-count")
def request_count_summary(
    service_name: str | None = Query(default=None, min_length=1),
    start_time: datetime | None = Query(default=None),
    end_time: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
):
    """Return summed request_count values."""

    if start_time and end_time and start_time > end_time:
        raise HTTPException(
            status_code=422,
            detail="start_time must be earlier than or equal to end_time",
        )

    total = get_request_count(
        db,
        service_name=service_name,
        start_time=start_time,
        end_time=end_time,
    )

    return {
        "service_name": service_name,
        "request_count": total,
        "start_time": start_time,
        "end_time": end_time,
    }


@router.get("/summary/error-rate")
def error_rate_summary(
    service_name: str = Query(..., min_length=1),
    start_time: datetime | None = Query(default=None),
    end_time: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
):
    """Return error rate as a percentage for one service."""

    if start_time and end_time and start_time > end_time:
        raise HTTPException(
            status_code=422,
            detail="start_time must be earlier than or equal to end_time",
        )

    rate = get_error_rate(
        db,
        service_name=service_name,
        start_time=start_time,
        end_time=end_time,
    )

    return {
        "service_name": service_name,
        "error_rate_percent": rate,
        "start_time": start_time,
        "end_time": end_time,
    }


@router.get("/summary/latency")
def latency_summary(
    service_name: str | None = Query(default=None, min_length=1),
    start_time: datetime | None = Query(default=None),
    end_time: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
):
    """Return average request_latency values."""

    if start_time and end_time and start_time > end_time:
        raise HTTPException(
            status_code=422,
            detail="start_time must be earlier than or equal to end_time",
        )

    average = get_average_latency(
        db,
        service_name=service_name,
        start_time=start_time,
        end_time=end_time,
    )

    return {
        "service_name": service_name,
        "average_latency": average,
        "unit": "ms",
        "start_time": start_time,
        "end_time": end_time,
    }


@router.get("/summary/grouped")
def grouped_metrics_summary(
    start_time: datetime | None = Query(default=None),
    end_time: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
):
    """Return aggregated metric values grouped by service and metric."""

    if start_time and end_time and start_time > end_time:
        raise HTTPException(
            status_code=422,
            detail="start_time must be earlier than or equal to end_time",
        )

    return {
        "items": group_metrics_by_service(
            db,
            start_time=start_time,
            end_time=end_time,
        )
    }


@router.get("/{metric_id}", response_model=MetricRecordResponse)
def get_metric(
    metric_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
):
    """Retrieve one metric record by its database ID."""

    record = get_metric_by_id(db, metric_id)

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Metric record not found",
        )

    return record
