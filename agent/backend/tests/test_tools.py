import pytest
from unittest.mock import patch, MagicMock
from app.tools import grafana_query

@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setenv("GRAFANA_URL", "https://mock.grafana.net")
    monkeypatch.setenv("GRAFANA_API_KEY", "glsa_mock_key_12345678901234567890123456789012")

def test_grafana_query_missing_credentials(monkeypatch):
    monkeypatch.delenv("GRAFANA_URL", raising=False)
    monkeypatch.delenv("GRAFANA_API_KEY", raising=False)
    
    # Reload or override module vars
    with patch("app.tools.GRAFANA_URL", ""), patch("app.tools.GRAFANA_API_KEY", ""):
        res = grafana_query("up", "promql")
        assert res["status"] == "error"
        assert "missing" in res["message"].lower()

def test_grafana_query_promql_success(mock_env):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"status": "success", "data": {"resultType": "vector", "result": []}}

    with patch("requests.get", return_value=mock_resp) as mock_get:
        res = grafana_query("shotops_investigations_total", "promql")
        assert res["status"] == "success"
        assert res["query_type"] == "promql"
        mock_get.assert_called_once()
        assert "grafanacloud-prom" in mock_get.call_args[0][0]

def test_grafana_query_logql_endpoint(mock_env):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"status": "success", "data": {"result": []}}

    with patch("requests.get", return_value=mock_resp) as mock_get:
        res = grafana_query('{service_name="backend"}', "logql")
        assert res["status"] == "success"
        assert res["query_type"] == "logql"
        assert "query_range" in mock_get.call_args[0][0]
        assert "grafanacloud-logs" in mock_get.call_args[0][0]

def test_grafana_query_unsupported_type(mock_env):
    res = grafana_query("query", "unsupported_type")
    assert res["status"] == "error"
    assert "Unsupported query_type" in res["message"]
