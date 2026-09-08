import os
import time
import logging
from dotenv import load_dotenv

load_dotenv(override=True)

endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "").rstrip("/")
headers_str = os.getenv("OTEL_EXPORTER_OTLP_HEADERS", "")

headers = {}
if headers_str:
    for item in headers_str.split(","):
        if "=" in item:
            k, v = item.split("=", 1)
            headers[k.strip()] = v.strip()

from opentelemetry.sdk.resources import Resource
from opentelemetry import trace
from opentelemetry.trace.status import Status, StatusCode
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter

from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter

resource = Resource.create({
    "service.name": "shotops-backend",
    "environment": "production"
})

# 1. TRACE SETUP
tracer_provider = TracerProvider(resource=resource)
trace_exporter = OTLPSpanExporter(endpoint=f"{endpoint}/v1/traces", headers=headers)
tracer_provider.add_span_processor(BatchSpanProcessor(trace_exporter))
trace.set_tracer_provider(tracer_provider)
tracer = trace.get_tracer("shotops.render.tracer")

# 2. METRIC SETUP
metric_exporter = OTLPMetricExporter(endpoint=f"{endpoint}/v1/metrics", headers=headers)
reader = PeriodicExportingMetricReader(metric_exporter)
meter_provider = MeterProvider(resource=resource, metric_readers=[reader])
metrics.set_meter_provider(meter_provider)
meter = metrics.get_meter("shotops.render.meter")

error_counter = meter.create_counter(
    "shotops_render_errors_total",
    description="Total render worker failures",
    unit="1"
)

# 3. LOG SETUP
logger_provider = LoggerProvider(resource=resource)
set_logger_provider(logger_provider)
log_exporter = OTLPLogExporter(endpoint=f"{endpoint}/v1/logs", headers=headers)
logger_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))
logger = logging.getLogger("shotops.render.pipeline")
logger.setLevel(logging.ERROR)
logger.addHandler(LoggingHandler(logger_provider=logger_provider))

# SIMULATE INCIDENT
print(f"Target OTLP Endpoint: {endpoint}")
print(f"Configured Header Keys: {list(headers.keys())}")
print("Simulating incident: CUDA Denoiser OOM on Sequence SQ_042...")

with tracer.start_as_current_span("render_sequence_sq042") as span:
    trace_id = format(span.get_span_context().trace_id, "032x")
    span.set_attribute("shot.sequence", "SQ_042")
    span.set_attribute("shot.frame_range", "1001-1250")
    span.set_attribute("worker.node_id", "worker-gpu-04")
    
    time.sleep(1)
    
    span.set_status(Status(StatusCode.ERROR, "CUDA out of memory in neural denoiser stage"))
    
    # Emit error metric
    error_counter.add(5, {
        "sequence": "SQ_042",
        "error_type": "OutOfMemoryError",
        "environment": "production"
    })
    print("✓ Recorded metric: shotops_render_errors_total (+5)")

    # Emit correlated error log
    err_msg = (
        f"[CRITICAL] Render worker worker-gpu-04 crashed on sequence SQ_042. "
        f"RuntimeError: CUDA out of memory. Tried to allocate 14.50 GiB (GPU 0; 16.00 GiB total capacity; "
        f"15.10 GiB already allocated). Trace ID: {trace_id}"
    )
    logger.error(err_msg)
    print(f"✓ Sent error log to Loki: {err_msg}")

# Flush all pipelines
tracer_provider.force_flush()
print("✓ Flushed trace exporter")
meter_provider.force_flush()
print("✓ Flushed metric exporter")
logger_provider.force_flush()
print("✓ Flushed log exporter")

print(f"\nIncident dispatched successfully. Correlated Trace ID: {trace_id}")
