from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from app.server import app

client = TestClient(app)

def test_create_investigation():
    with patch("app.runner.ADKRunner.run_investigation", new_callable=AsyncMock):
        response = client.post("/investigations", json={"query": "Test query for telemetry"})
        assert response.status_code == 200
        data = response.json()
        assert "investigationId" in data
        assert data["status"] == "running"

def test_investigation_not_found():
    response = client.get("/investigations/nonexistent-id/events")
    assert response.status_code == 404
