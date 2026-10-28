
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from shared.tracing import configure_tracing
from services.telemetry_ingestion.app.routers.ingestion import (
    router as ingestion_router,
)
from services.telemetry_ingestion.app.routers.traces import (
    router as traces_router,
)
from services.telemetry_ingestion.app.routers.logs import (
    router as logs_router,
)
from services.telemetry_ingestion.app.routers.metrics import (
    router as metrics_router,
)
from services.telemetry_ingestion.app.routers.alerts import (
    router as alerts_router,
)
from services.telemetry_ingestion.app.routers.root_cause import (
    router as root_cause_router,
)

from services.telemetry_ingestion.app.routers.service_map import (
    router as service_map_router,
)

from services.telemetry_ingestion.app.routers.workspace_settings import (
    router as workspace_settings_router,
)


configure_tracing("telemetry-ingestion")

app = FastAPI(
    title="Telemetry Ingestion Service",
    description=(
        "Receives and stores telemetry events "
        "for the Distributed Observability Platform."
    ),
    version="1.0.0",
)

# Allow the local React/Vite frontend to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5177",
        "http://127.0.0.1:5177",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "telemetry-ingestion",
    }


app.include_router(ingestion_router)
app.include_router(traces_router)
app.include_router(logs_router)
app.include_router(metrics_router)
app.include_router(alerts_router)
app.include_router(root_cause_router)
app.include_router(service_map_router)

FastAPIInstrumentor.instrument_app(app)
app.include_router(workspace_settings_router)
