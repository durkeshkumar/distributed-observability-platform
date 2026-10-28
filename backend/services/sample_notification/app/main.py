
from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from shared.tracing import configure_tracing
from services.sample_notification.app.routers.notifications import (
    router as notifications_router,
)

configure_tracing("sample-notification")

app = FastAPI(
    title="Sample Notification Service",
    description="Demonstration notification microservice for distributed observability.",
    version="1.0.0",
)


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "sample-notification",
    }


app.include_router(notifications_router)
FastAPIInstrumentor.instrument_app(app)
