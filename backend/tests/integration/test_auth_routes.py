"""
Integration tests for authentication routes.
"""

from fastapi.testclient import TestClient
from backend.src.domain.entities.member import MemberTokensDTO


def test_login_success(client: TestClient, container) -> None:
    """
    Test successful login route returns access and refresh tokens.
    """
    container.auth_use_case.login.return_value = MemberTokensDTO(access_token="access", refresh_token="refresh")
    response = client.post("/auth/login", json={"mail": "user@mail.com", "password": "pass"})
    assert response.status_code == 200
    assert response.json()["access_token"] == "access"
    assert response.json()["refresh_token"] == "refresh"
    container.auth_use_case.login.assert_called_once()


def test_refresh_success(client: TestClient, container) -> None:
    """
    Test refresh route returns new access and refresh tokens.
    """
    container.auth_use_case.refresh.return_value = MemberTokensDTO(access_token="access2", refresh_token="refresh2")
    response = client.post("/auth/refresh?refresh_token=refresh")
    assert response.status_code == 200
    assert response.json()["access_token"] == "access2"
    assert response.json()["refresh_token"] == "refresh2"
    container.auth_use_case.refresh.assert_called_once()


def test_logout_success(client: TestClient, container) -> None:
    """
    Test logout route returns 200 and calls logout on the service.
    """
    container.auth_use_case.logout.return_value = None
    response = client.post("/auth/logout?refresh_token=refresh")
    assert response.status_code == 200
    container.auth_use_case.logout.assert_called_once()
