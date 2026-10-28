
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)


def configure_tracing(service_name: str) -> None:
    current_provider = trace.get_tracer_provider()

    # Avoid configuring the global provider more than once
    if isinstance(current_provider, TracerProvider):
        return

    resource = Resource.create(
        {
            "service.name": service_name,
            "service.namespace": "distributed-observability-platform",
        }
    )

    provider = TracerProvider(resource=resource)
    provider.add_span_processor(
        BatchSpanProcessor(ConsoleSpanExporter())
    )

    trace.set_tracer_provider(provider)
