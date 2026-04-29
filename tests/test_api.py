import pytest
from fastapi.testclient import TestClient
from api.main import app
from config.settings import settings

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data

def test_auth_middleware_missing_key():
    response = client.get("/api/agent/status")
    # In simulation mode it allows it, in production it should be 401
    if not settings.simulation_mode and not settings.debug:
        assert response.status_code == 401

def test_auth_middleware_valid_key():
    response = client.get("/api/agent/status", headers={"X-API-Key": settings.api_key})
    assert response.status_code == 200
    assert "status" in response.json()

def test_webhook_github():
    response = client.post(
        "/webhook/github",
        headers={"X-GitHub-Event": "push"},
        json={"ref": "refs/heads/main"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "received"
