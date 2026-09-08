# ShotOps 🎬⚡

> Autonomous AI Production Operations Director for Film & VFX Pipelines  
> Powered by Google Gemini ADK, FastAPI, and Grafana Cloud (Prometheus, Loki, Tempo).

«Your production has a problem. ShotOps finds out why.»

---

## Overview

Modern VFX and virtual production facilities run continuous compute clusters where asset pipelines, render workers, and composite jobs generate thousands of concurrent events. When a render sequence fails, pinpointing the breakdown across metrics, logs, and distributed trace spans often takes hours of manual correlation.

**ShotOps** automates incident triage in active VFX production environments (such as **SHADOW PROTOCOL**). It acts as an autonomous operations director that:
* **Monitors Core Pipeline Health:** Detects error spikes in Prometheus with automated lookback resilience (`last_over_time`) for idle and bursty workers.
* **Isolates Failing Context in Loki:** Parses unstructured logs using indexed resource stream labels (`{service_name="shotops-backend"}`) and line filters (`|= "SQ_042"`), identifying worker nodes and hardware errors.
* **Correlates Distributed Traces in Tempo:** Extracts hex Trace IDs from logs to inspect exact span timings, execution phases, and error statuses.
* **Delivers Actionable Remediation:** Generates structured executive postmortems and embeds direct deep links into Grafana Explore.

---

## Architecture

```
[ VFX Pipeline / Render Workers ]
               │ (OTLP: Metrics, Logs, Spans)
               ▼
      [ Grafana Cloud ]
   ┌───────────┼───────────┐
   │           │           │
Prometheus   Loki        Tempo
(Metrics)   (Logs)      (Traces)
   └───────────┼───────────┘
               │ (Grafana Query Proxy)
               ▼
     [ ShotOps Agent API ] (FastAPI + Google Gemini ADK)
               │ (Server-Sent Events)
               ▼
     [ ShotOps Ops Console ] (Dark/Gold Real-Time Dashboard)
```

### Technical Stack
* **Agent Core:** Google Gemini ADK (`gemini-2.5-flash`) utilizing multi-signal tool dispatch.
* **Telemetry Ingestion:** OpenTelemetry (OTLP) exporting metrics, logs, and traces to Grafana Cloud.
* **Backend Framework:** FastAPI with asynchronous Server-Sent Events (SSE) streaming.
* **Frontend Console:** Dark/gold operations console with live event timelines, quick-action prompt chips, and styled Markdown reporting.

---

## Incident Case Study: SHADOW PROTOCOL Sequence SQ_042

ShotOps includes an end-to-end incident simulator (`simulate_incident.py`):
1. **The Event:** A production render job on sequence `SQ_042` crashes during the neural denoiser stage.
2. **Metric Signal:** `shotops_render_errors_total` records a spike of 5 errors labeled `error_type="OutOfMemoryError"`.
3. **Log Signal:** Loki surfaces critical stack traces from `worker-gpu-04`:
   `RuntimeError: CUDA out of memory. Tried to allocate 14.50 GiB (GPU 0; 16.00 GiB total capacity; 15.10 GiB already allocated)`.
4. **Trace Signal:** Tempo span `render_sequence_sq042` traces the failure to the denoiser pass and records execution duration (~1.0s).
5. **Resolution:** ShotOps recommends immediately cordoning `worker-gpu-04`, rerouting sequence `SQ_042` to 24GB+ GPU nodes, and tuning denoiser tile sizes.

---

## Quickstart Guide

### 1. Prerequisites & Environment
Ensure Python 3.11+ is installed. Create an `.env` file in `agent/backend/`:
```env
GOOGLE_API_KEY="your-gemini-api-key"
GEMINI_MODEL="gemini-2.5-flash"
GRAFANA_URL="https://your-stack.grafana.net"
GRAFANA_API_KEY="your-grafana-service-account-token"
OTEL_EXPORTER_OTLP_ENDPOINT="https://otlp-gateway-prod.grafana.net/otlp"
OTEL_EXPORTER_OTLP_HEADERS="Authorization=Basic <token>"
```

### 2. Run Test Suite
```bash
cd agent/backend
pytest -v
```

### 3. Launch Ops Console
```bash
uvicorn app.server:app --host 0.0.0.0 --port 8000 --reload
```
Open `http://localhost:8000` to interact with the ShotOps console.

### 4. Trigger Simulation
In a separate terminal:
```bash
python simulate_incident.py
```
Click the **SQ_042 OOM Failure** quick chip on the dashboard to initiate the automated investigation.

---

## Observability Best Practices Encoded
* **Lookback Fallback Resilience:** Instant Prometheus queries default to 5 minutes; ShotOps automatically queries `last_over_time(<metric>[1h])` when vector streams are stale.
* **High-Cardinality Loki Queries:** Prevents label index explosions by restricting stream selectors to service resource tags and using line matchers (`|=`) for dynamic fields.
* **One-Click Triage:** Generated reports automatically build Grafana Explore URLs for immediate manual inspection of raw traces and log lines.
