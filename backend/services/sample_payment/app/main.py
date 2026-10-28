
from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from shared.tracing import configure_tracing
from services.sample_payment.app.routers.payments import router as payments_router

configure_tracing("sample-payment")

app = FastAPI(
    title="Sample Payment Service",
    description="Demonstration payment microservice for distributed observability.",
    version="1.0.0",
)


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "sample-payment",
    }


app.include_router(payments_router)
FastAPIInstrumentor.instrument_app(app)
