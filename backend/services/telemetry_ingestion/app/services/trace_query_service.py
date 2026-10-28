
from sqlalchemy.orm import Session

from services.telemetry_ingestion.app.models import TraceSpan


def get_trace_spans(db: Session, trace_id: str) -> list[TraceSpan]:
    """Return all spans for a trace in start-time order."""
    return (
        db.query(TraceSpan)
        .filter(TraceSpan.trace_id == trace_id)
        .order_by(TraceSpan.start_time.asc(), TraceSpan.id.asc())
        .all()
    )
