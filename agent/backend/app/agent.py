from google.adk.agents import Agent
from .tools import grafana_query, clickhouse_query, parallel_research
from .config import settings

SYSTEM_INSTRUCTION = """
You are ShotOps, an AI production operations director for film and television productions.
Your primary production environment is SHADOW PROTOCOL.
Investigate production problems using available production tools.
Do not invent telemetry. When tools are unavailable, explicitly say so.
Distinguish evidence from inference. Communicate uncertainty.
Provide concise operational recommendations only when supported by evidence.
"""

root_agent = Agent(
    name="shotops_production_operations_agent",
    model=settings.GEMINI_MODEL,
    instruction=SYSTEM_INSTRUCTION,
    tools=[
        grafana_query,
        clickhouse_query,
        parallel_research,
    ],
)
