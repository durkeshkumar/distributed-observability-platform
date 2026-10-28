
from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

from shared.tracing import configure_tracing
from services.api_gateway.app.routers.ingestion_proxy import (
    router as ingestion_proxy_router,
)

configure_tracing("api-gateway")

app = FastAPI(
    title="Observability API Gateway",
    description=(
        "API Gateway for the Distributed Observability "
        "and Root-Cause Analysis Platform."
    ),
    version="1.0.0",
)


@app.get("/", tags=["General"])
def root():
    return {
        "message": "Welcome to the Observability API Gateway",
        "service": "api-gateway",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "api-gateway",
    }


app.include_router(ingestion_proxy_router)

FastAPIInstrumentor.instrument_app(app)
HTTPXClientInstrumentor().instrument()
