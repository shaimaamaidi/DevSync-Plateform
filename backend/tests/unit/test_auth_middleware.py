"""Unit tests for JWTAuthMiddleware."""

from unittest.mock import MagicMock
import pytest
from fastapi import Request
from backend.src.presentation.api.middleware.auth_middleware import JWTAuthMiddleware


def test_public_path_skips_auth():
    app = MagicMock()
    middleware = JWTAuthMiddleware(app)
    request = MagicMock(spec=Request)
    request.url.path = "/auth/login"
    response = pytest.run(middleware.dispatch(request, MagicMock()))
    assert response is not None
