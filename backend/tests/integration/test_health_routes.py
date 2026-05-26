"""
Integration tests for health routes.
"""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.src.presentation.api.routers import health_router


def test_health_check_returns_ok() -> None:
    """
    Test that the health route returns the service status.
    """
    app = FastAPI()
    app.include_router(health_router.router, prefix="/health", tags=["health"])
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
