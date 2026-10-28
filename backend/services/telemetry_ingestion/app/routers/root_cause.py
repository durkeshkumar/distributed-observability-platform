
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session

from shared.database import get_db
from services.telemetry_ingestion.app.schemas.root_cause import (
    RootCauseReportResponse,
)
from services.telemetry_ingestion.app.services.root_cause_diagnostic_service import (
    analyze_root_cause,
)
from services.telemetry_ingestion.app.services.telemetry_correlation_service import (
    correlate_trace_telemetry,
)

router = APIRouter(
    prefix="/root-cause",
    tags=["Root-Cause Analysis"],
)


@router.get(
    "/{trace_id}",
    response_model=RootCauseReportResponse,
)
def get_root_cause_report(
    trace_id: str = Path(min_length=1, max_length=100),
    db: Session = Depends(get_db),
):
    trace_id = trace_id.strip()

    if not trace_id:
        raise HTTPException(
            status_code=400,
            detail="trace_id must not be empty",
        )

    try:
        correlation_data = correlate_trace_telemetry(
            db,
            trace_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    if correlation_data["span_count"] == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Trace '{trace_id}' was not found",
        )

    return analyze_root_cause(correlation_data)
