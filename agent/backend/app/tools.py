from google.adk.tools import tool

@tool
def grafana_query(query: str) -> dict:
    return {
        "status": "unavailable",
        "tool": "grafana",
        "message": "Grafana integration is not connected in Phase 3A."
    }

@tool
def clickhouse_query(query: str) -> dict:
    return {
        "status": "unavailable",
        "tool": "clickhouse",
        "message": "ClickHouse integration is not connected in Phase 3A."
    }

@tool
def parallel_research(topic: str) -> dict:
    return {
        "status": "unavailable",
        "tool": "parallel",
        "message": "Parallel integration is not connected in Phase 3A."
    }
