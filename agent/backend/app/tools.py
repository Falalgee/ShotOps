import os
import requests
from dotenv import load_dotenv

load_dotenv(override=True)

GRAFANA_URL = os.getenv("GRAFANA_URL", "").rstrip("/")
GRAFANA_API_KEY = os.getenv("GRAFANA_API_KEY", "")

PROMETHEUS_UID = "grafanacloud-prom"
LOKI_UID = "grafanacloud-logs"
TEMPO_UID = "grafanacloud-traces"

def grafana_query(query: str, query_type: str = "promql") -> dict:
    """
    Executes an observability query against Grafana Cloud.
    
    Args:
        query: PromQL expression, LogQL query, or a Tempo Trace ID.
        query_type: 'promql' (metrics), 'logql' (logs), or 'tempo' (traces).
    """
    if not GRAFANA_URL or not GRAFANA_API_KEY:
        return {"status": "error", "message": "Grafana credentials missing in environment."}

    headers = {"Authorization": f"Bearer {GRAFANA_API_KEY}"}
    qtype = query_type.lower().strip()

    try:
        if qtype in ["promql", "metrics", "prometheus"]:
            url = f"{GRAFANA_URL}/api/datasources/proxy/uid/{PROMETHEUS_UID}/api/v1/query"
            resp = requests.get(url, headers=headers, params={"query": query}, timeout=15)
        elif qtype in ["logql", "logs", "loki"]:
            url = f"{GRAFANA_URL}/api/datasources/proxy/uid/{LOKI_UID}/loki/api/v1/query_range"
            resp = requests.get(url, headers=headers, params={"query": query, "limit": 20}, timeout=15)
        elif qtype in ["tempo", "traces", "trace"]:
            url = f"{GRAFANA_URL}/api/datasources/proxy/uid/{TEMPO_UID}/api/traces/{query}"
            resp = requests.get(url, headers=headers, timeout=15)
        else:
            return {
                "status": "error",
                "message": f"Unsupported query_type '{query_type}'. Use 'promql', 'logql', or 'tempo'."
            }

        if resp.status_code == 200:
            return {"status": "success", "query_type": qtype, "data": resp.json()}
        return {"status": "error", "http_status": resp.status_code, "message": resp.text[:300]}
    except Exception as e:
        return {"status": "error", "message": str(e)}
