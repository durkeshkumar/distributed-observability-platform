
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session

from shared.database import get_db
from services.telemetry_ingestion.app.schemas.trace import TraceSpanResponse
from services.telemetry_ingestion.app.services.trace_query_service import (
    get_trace_spans,
)
from services.telemetry_ingestion.app.models import TraceSpan


router = APIRouter(prefix="/traces", tags=["Trace Processing"])


@router.get("", response_model=list[TraceSpanResponse])
def list_traces(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    """Return stored trace spans, newest first."""
    return (
        db.query(TraceSpan)
        .order_by(TraceSpan.start_time.desc(), TraceSpan.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


@router.get("/{trace_id}", response_model=list[TraceSpanResponse])
def retrieve_trace(
    trace_id: str = Path(min_length=1, max_length=100),
    db: Session = Depends(get_db),
):
    """Return all spans belonging to one trace."""
    trace_id = trace_id.strip()

    if not trace_id:
        raise HTTPException(
            status_code=400,
            detail="trace_id must not be empty",
        )

    spans = get_trace_spans(db, trace_id)

    if not spans:
        raise HTTPException(
            status_code=404,
            detail="Trace not found",
        )

    return spans
