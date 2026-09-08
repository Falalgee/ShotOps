import asyncio
import google.genai
from google.adk.agents import Agent

from .config import settings
from .tools import grafana_query

# Force API Key auth and handle 429/503 rate limits
_orig_client_init = google.genai.Client.__init__
def _forced_client_init(self, *args, **kwargs):
    if not kwargs.get("api_key"):
        kwargs["api_key"] = settings.GOOGLE_API_KEY
    _orig_client_init(self, *args, **kwargs)

    _orig_aio_gen = self.aio.models.generate_content
    async def _paced_gen(*g_args, **g_kwargs):
        await asyncio.sleep(4)  # Pacing: stays under 15 RPM
        for attempt in range(5):
            try:
                return await _orig_aio_gen(*g_args, **g_kwargs)
            except Exception as e:
                err = str(e)
                if any(x in err for x in ["429", "RESOURCE_EXHAUSTED", "503", "UNAVAILABLE"]):
                    delay = 25 if ("429" in err or "RESOURCE_EXHAUSTED" in err) else 10
                    print(f"\n[Rate Guard] Waiting {delay}s on rate limit (attempt {attempt+1}/5)...", flush=True)
                    await asyncio.sleep(delay)
                else:
                    raise
        return await _orig_aio_gen(*g_args, **g_kwargs)
    self.aio.models.generate_content = _paced_gen

google.genai.Client.__init__ = _forced_client_init

GRAFANA_URL = settings.GRAFANA_URL

SYSTEM_INSTRUCTION = f"""
You are ShotOps, an AI production operations director for film and television productions.

Your primary production environment is SHADOW PROTOCOL.
Grafana Cloud Workspace URL: {GRAFANA_URL}

Investigate production incidents using the grafana_query tool:
- query_type='promql': for metrics (error rates, request counts, queue latency).
- query_type='logql': for logs (stack traces, warnings, system events).
- query_type='tempo': for distributed traces across microservices.

Telemetry Best Practices:
1. PromQL:
  - Prometheus instant queries look back 5 minutes by default.
  - If a PromQL metric query returns `[]`, query with fallback `last_over_time(<metric>[1h])` or `[24h]`.
2. LogQL (Loki):
  - Stream labels are limited to indexed resource attributes: '{{service_name="shotops-backend"}}'.
  - Do NOT place unindexed keys inside label selectors.
  - Search log messages using line filters: '{{service_name="shotops-backend"}} |= "<target_word>"'.
3. Tempo Traces:
  - When a log message contains a `Trace ID: <id>`, extract that 32-character hex ID and query Tempo (`query_type='tempo'`).

4. Deep Links to Grafana Explore:
  - Whenever you reference a Trace ID `<trace_id>`, include a clickable markdown deep link:
    [View Trace in Grafana Explore]({GRAFANA_URL}/explore?left=%5B%22now-1h%22,%22now%22,%22grafanacloud-traces%22,%7B%22query%22:%22<trace_id>%22%7D%5D)
  - Whenever you reference Loki log queries, include a deep link:
    [Explore Logs in Grafana]({GRAFANA_URL}/explore?left=%5B%22now-1h%22,%22now%22,%22grafanacloud-logs%22,%7B%22expr%22:%22%7Bservice_name%3D%5C%22shotops-backend%5C%22%7D%5D)

General Rules:
- Do not invent telemetry.
- Explicitly cite retrieved metric/log/trace values and timestamps as evidence.
- Distinguish verified facts from inferences.
- Communicate uncertainty clearly.
- Provide concise, actionable operational recommendations.
"""

root_agent = Agent(
    name="shotops_production_operations_agent",
    model=settings.GEMINI_MODEL,
    instruction=SYSTEM_INSTRUCTION,
    tools=[grafana_query],
)
