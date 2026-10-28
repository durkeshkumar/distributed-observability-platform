
from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

from shared.tracing import configure_tracing
from services.sample_order.app.routers.orders import router as orders_router

configure_tracing("sample-order")

app = FastAPI(
    title="Sample Order Service",
    description="Coordinates order processing, payments, and notifications.",
    version="1.0.0",
)


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "sample-order",
    }


app.include_router(orders_router)
FastAPIInstrumentor.instrument_app(app)
HTTPXClientInstrumentor().instrument()
