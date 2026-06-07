"""
Unit tests for JWT authentication middleware.
"""

from contextlib import nullcontext
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from starlette.responses import Response

import sys
import types

_dummy_persistence = types.ModuleType("backend.src.infrastructure.di.persistence_container")
_dummy_persistence.PersistenceContainer = lambda session: None
_dummy_persistence.Container = _dummy_persistence.PersistenceContainer
sys.modules["backend.src.infrastructure.di.persistence_container"] = _dummy_persistence

from backend.src.domain.exceptions.auth.invalid_token_exception import InvalidTokenException
from backend.src.presentation.api.middleware.auth_middleware import JWTAuthMiddleware

# Remove the temporary stub so other tests import the real module
if "backend.src.infrastructure.di.persistence_container" in sys.modules:
    del sys.modules["backend.src.infrastructure.di.persistence_container"]


class _FakeContainer:
    """
    Minimal container stub exposing a JWT handler.
    """

    def __init__(self, session, jwt_handler: MagicMock) -> None:
        self.session = session
        self.jwt_handler = jwt_handler


class _FakeRequest:
    """
    Minimal request stub for middleware tests.
    """

    def __init__(self, path: str, method: str = "GET", headers: dict | None = None, cookies: dict | None = None) -> None:
        self.url = SimpleNamespace(path=path)
        self.method = method
        self.headers = headers or {}
        self.cookies = cookies or {}
        self.state = SimpleNamespace()
        self.app = SimpleNamespace(state=SimpleNamespace(db=MagicMock()))


@pytest.mark.asyncio
async def test_dispatch_skips_public_paths() -> None:
    """
    Test that public paths bypass JWT verification.
    """
    request = _FakeRequest("/auth/login")
    call_next = AsyncMock(return_value=Response("ok"))
    middleware = JWTAuthMiddleware(app=MagicMock())

    response = await middleware.dispatch(request, call_next)

    assert response.status_code == 200
    call_next.assert_awaited_once_with(request)
    request.app.state.db.get_session.assert_not_called()


@pytest.mark.asyncio
async def test_dispatch_returns_401_when_token_is_missing() -> None:
    """
    Test that protected paths reject requests without a token.
    """
    request = _FakeRequest("/repo")
    call_next = AsyncMock(return_value=Response("ok"))
    middleware = JWTAuthMiddleware(app=MagicMock())

    response = await middleware.dispatch(request, call_next)

    import json

    assert response.status_code == 401
    assert response.headers.get("WWW-Authenticate") == "Bearer"
    assert json.loads(response.body)["error"]["code"] == "UNAUTHORIZED"
    call_next.assert_not_awaited()
    request.app.state.db.get_session.assert_not_called()


@pytest.mark.asyncio
async def test_dispatch_verifies_bearer_token(monkeypatch) -> None:
    """
    Test that a valid bearer token is verified and attached to request state.
    """
    request = _FakeRequest("/repo", headers={"Authorization": "Bearer test-token"})
    call_next = AsyncMock(return_value=Response("ok"))
    session = MagicMock()
    request.app.state.db.get_session.return_value = nullcontext(session)

    jwt_handler = MagicMock()
    jwt_handler.verify_token.return_value = {"sub": "member-1"}

    monkeypatch.setattr(
        "backend.src.presentation.api.middleware.auth_middleware.PersistenceContainer",
        lambda _session: _FakeContainer(_session, jwt_handler),
    )

    middleware = JWTAuthMiddleware(app=MagicMock())
    response = await middleware.dispatch(request, call_next)

    assert response.status_code == 200
    assert request.state.current_member == {"sub": "member-1"}
    jwt_handler.verify_token.assert_called_once_with("test-token")
    call_next.assert_awaited_once_with(request)
    request.app.state.db.get_session.assert_called_once()


@pytest.mark.asyncio
async def test_dispatch_returns_401_for_invalid_token(monkeypatch) -> None:
    """
    Test that invalid tokens are converted into an unauthorized response.
    """
    request = _FakeRequest("/repo", headers={"Authorization": "Bearer invalid-token"})
    call_next = AsyncMock(return_value=Response("ok"))
    session = MagicMock()
    request.app.state.db.get_session.return_value = nullcontext(session)

    jwt_handler = MagicMock()
    jwt_handler.verify_token.side_effect = InvalidTokenException("Session is invalid. Please log in again.")

    monkeypatch.setattr(
        "backend.src.presentation.api.middleware.auth_middleware.PersistenceContainer",
        lambda _session: _FakeContainer(_session, jwt_handler),
    )

    middleware = JWTAuthMiddleware(app=MagicMock())
    response = await middleware.dispatch(request, call_next)

    import json

    assert response.status_code == 401
    assert json.loads(response.body)["error"]["code"] == "INVALID_TOKEN"
    call_next.assert_not_awaited()
    jwt_handler.verify_token.assert_called_once_with("invalid-token")


@pytest.mark.asyncio
async def test_dispatch_verifies_cookie_token(monkeypatch) -> None:
    """
    Test that the middleware accepts an access_token cookie when no bearer token is present.
    """
    request = _FakeRequest("/repo", cookies={"access_token": "cookie-token"})
    call_next = AsyncMock(return_value=Response("ok"))
    session = MagicMock()
    request.app.state.db.get_session.return_value = nullcontext(session)

    jwt_handler = MagicMock()
    jwt_handler.verify_token.return_value = {"sub": "member-2"}

    monkeypatch.setattr(
        "backend.src.presentation.api.middleware.auth_middleware.PersistenceContainer",
        lambda _session: _FakeContainer(_session, jwt_handler),
    )

    middleware = JWTAuthMiddleware(app=MagicMock())
    response = await middleware.dispatch(request, call_next)

    assert response.status_code == 200
    assert request.state.current_member == {"sub": "member-2"}
    jwt_handler.verify_token.assert_called_once_with("cookie-token")
    call_next.assert_awaited_once_with(request)
    request.app.state.db.get_session.assert_called_once()


@pytest.mark.asyncio
async def test_dispatch_allows_options_requests(monkeypatch) -> None:
    """
    Test that OPTIONS requests bypass JWT verification.
    """
    request = _FakeRequest("/repo", method="OPTIONS")
    call_next = AsyncMock(return_value=Response("ok"))
    middleware = JWTAuthMiddleware(app=MagicMock())

    response = await middleware.dispatch(request, call_next)

    assert response.status_code == 200
    call_next.assert_awaited_once_with(request)
