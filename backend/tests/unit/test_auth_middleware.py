"""
Unit tests for JWTAuthMiddleware.
"""

import asyncio
from unittest.mock import MagicMock
from starlette.requests import Request as StarletteRequest

from backend.src.presentation.api.middleware.auth_middleware import JWTAuthMiddleware


def test_public_path_skips_auth():
    """
    Test that the JWTAuthMiddleware skips authentication for public paths like /auth/login.
    """
    app = MagicMock()
    middleware = JWTAuthMiddleware(app)
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/auth/login",
        "headers": [],
        "query_string": b"",
        "server": ("testserver", 80),
        "client": ("testclient", 123),
        "scheme": "http",
    }
    request = StarletteRequest(scope)

    async def call_next(req):
        return "called"

    response = asyncio.run(middleware.dispatch(request, call_next))
    assert response == "called"
