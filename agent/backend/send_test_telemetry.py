import os
import time
import logging
from dotenv import load_dotenv

load_dotenv(override=True)

endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "").rstrip("/")
headers_str = os.getenv("OTEL_EXPORTER_OTLP_HEADERS", "")

# Parse headers dictionary
headers = {}
if headers_str:
    for item in headers_str.split(","):
        if "=" in item:
            k, v = item.split("=", 1)
            headers[k.strip()] = v.strip()

print(f"Target OTLP Endpoint: {endpoint}")
print(f"Configured Header Keys: {list(headers.keys())}")

from opentelemetry.sdk.resources import Resource
resource = Resource.create({"service.name": "shotops-backend", "environment": "production"})

# 1. TRACE (shotops.grafana.integration)
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

tracer_provider = TracerProvider(resource=resource)
trace_exporter = OTLPSpanExporter(
    endpoint=f"{endpoint}/v1/traces",
    headers=headers
)
tracer_provider.add_span_processor(BatchSpanProcessor(trace_exporter))
trace.set_tracer_provider(tracer_provider)
tracer = trace.get_tracer("shotops.tracer")

with tracer.start_as_current_span("shotops.grafana.integration") as span:
    span.set_attribute("shotops.phase", "3B")
    span.set_attribute("test.status", "active")
    print("✓ Created trace span: shotops.grafana.integration")

tracer_provider.force_flush()
print("✓ Flushed trace exporter")

# 2. METRIC (shotops_investigations_total)
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter

metric_exporter = OTLPMetricExporter(
    endpoint=f"{endpoint}/v1/metrics",
    headers=headers
)
reader = PeriodicExportingMetricReader(metric_exporter)
meter_provider = MeterProvider(resource=resource, metric_readers=[reader])
metrics.set_meter_provider(meter_provider)
meter = metrics.get_meter("shotops.meter")

counter = meter.create_counter(
    "shotops_investigations_total",
    description="Count of investigations executed by ShotOps",
    unit="1"
)
counter.add(1, {"investigation_type": "root_cause", "environment": "production"})
print("✓ Recorded metric: shotops_investigations_total (+1)")

meter_provider.force_flush()
print("✓ Flushed metric exporter")

# 3. LOG (ShotOps Grafana integration test)
try:
    from opentelemetry._logs import set_logger_provider
    from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
    from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
    from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter

    logger_provider = LoggerProvider(resource=resource)
    set_logger_provider(logger_provider)
    log_exporter = OTLPLogExporter(
        endpoint=f"{endpoint}/v1/logs",
        headers=headers
    )
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))
    
    logger = logging.getLogger("shotops.agent")
    logger.setLevel(logging.INFO)
    logger.addHandler(LoggingHandler(logger_provider=logger_provider))
    
    logger.info("ShotOps Grafana integration test log: verifying telemetry pipeline in Phase 3B")
    print("✓ Sent log message: 'ShotOps Grafana integration test'")
    
    logger_provider.force_flush()
    print("✓ Flushed log exporter")
except Exception as e:
    print(f"Log exporter error: {e}")

print("\nTelemetry dispatch complete.")
