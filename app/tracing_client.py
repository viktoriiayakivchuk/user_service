import os
import logging
from fastapi import FastAPI

logger = logging.getLogger("tracing_client")

try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.propagate import inject, extract
    from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
    
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False
    logger.warning("OpenTelemetry libraries not installed. Tracing is disabled.")

class TelemetryAgent:
    def __init__(self):
        self.tracer = None
        if OTEL_AVAILABLE:
            service_name = os.getenv("OTEL_SERVICE_NAME", "user-service")
            otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
            
            # Setup Resource
            resource = Resource.create(attributes={
                "service.name": service_name
            })
            
            # Setup Provider and Exporter
            provider = TracerProvider(resource=resource)
            try:
                otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
                processor = BatchSpanProcessor(otlp_exporter)
                provider.add_span_processor(processor)
                trace.set_tracer_provider(provider)
                self.tracer = trace.get_tracer(service_name)
                logger.info(f"OpenTelemetry tracing initialized exporting to {otlp_endpoint}")
            except Exception as e:
                logger.error(f"Failed to initialize OTLP Span Exporter: {e}")
                # Fallback to standard trace provider if initialization failed
                self.tracer = trace.get_tracer(service_name)
        else:
            self.tracer = None

    def instrument_app(self, app: FastAPI):
        if OTEL_AVAILABLE and self.tracer:
            try:
                FastAPIInstrumentor.instrument_app(app)
                logger.info("FastAPI application instrumented with OpenTelemetry.")
            except Exception as e:
                logger.error(f"Failed to instrument FastAPI application: {e}")

    def get_tracer(self):
        if OTEL_AVAILABLE and self.tracer:
            return self.tracer
        # Return mock / no-op tracer context manager if OTel is not available
        class MockTracer:
            def start_as_current_span(self, name, *args, **kwargs):
                from contextlib import nullcontext
                return nullcontext()
        return MockTracer()

    def inject_trace_context(self, headers: dict) -> dict:
        """Inject current span context into carrier dictionary for AMQP headers"""
        if OTEL_AVAILABLE:
            try:
                TraceContextTextMapPropagator().inject(headers)
            except Exception as e:
                logger.error(f"Failed to inject trace context: {e}")
        return headers

    def extract_trace_context(self, headers: dict):
        """Extract trace context from carrier dictionary"""
        if OTEL_AVAILABLE:
            try:
                return TraceContextTextMapPropagator().extract(headers)
            except Exception as e:
                logger.error(f"Failed to extract trace context: {e}")
        return None

tracing_client = TelemetryAgent()
