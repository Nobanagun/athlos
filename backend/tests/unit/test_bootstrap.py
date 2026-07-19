"""Smoke tests for the backend bootstrap (no domain logic involved)."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from athlos.api.main import app


def test_app_is_a_fastapi_instance() -> None:
    assert isinstance(app, FastAPI)


def test_health_endpoint_returns_ok() -> None:
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
