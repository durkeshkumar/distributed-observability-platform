
import httpx
from fastapi import HTTPException
from starlette.responses import Response

INGESTION_SERVICE_URL = "http://127.0.0.1:8001"


async def forward_ingestion_request(
    method: str,
    path: str,
    *,
    params: dict | None = None,
    payload: dict | None = None,
) -> Response:
    url = f"{INGESTION_SERVICE_URL}{path}"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            upstream = await client.request(
                method=method,
                url=url,
                params=params,
                json=payload,
            )

        return Response(
            content=upstream.content,
            status_code=upstream.status_code,
            media_type=upstream.headers.get("content-type"),
        )

    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=503,
            detail="Telemetry Ingestion Service is unavailable",
        ) from exc
