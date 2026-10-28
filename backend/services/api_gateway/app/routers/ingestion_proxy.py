
from fastapi import APIRouter, Query
from starlette.responses import Response

from services.api_gateway.app.services.ingestion_proxy import (
    forward_ingestion_request,
)

router = APIRouter(
    prefix="/api/ingestion",
    tags=["Ingestion Gateway"],
)


@router.post("/events")
async def create_event(payload: dict) -> Response:
    return await forward_ingestion_request(
        "POST",
        "/ingestion/events",
        payload=payload,
    )


@router.get("/events")
async def list_events(
    limit: int = Query(default=100, ge=1, le=500),
) -> Response:
    return await forward_ingestion_request(
        "GET",
        "/ingestion/events",
        params={"limit": limit},
    )


@router.get("/events/{event_id}")
async def get_event(event_id: str) -> Response:
    return await forward_ingestion_request(
        "GET",
        f"/ingestion/events/{event_id}",
    )
