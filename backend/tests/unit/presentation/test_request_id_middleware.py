"""
Unit tests for request id middleware.
"""

import pytest
from starlette.requests import Request
from starlette.responses import Response

from backend.src.infrastructure.logging.request_id import get_request_id
from backend.src.presentation.api.middleware.request_id_middleware import request_id_middleware


@pytest.mark.asyncio
async def test_request_id_middleware_uses_header_value() -> None:
    """
    Middleware should propagate incoming X-Request-Id header.
    """
    scope = {
        "type": "http",
        "headers": [(b"x-request-id", b"req-123")],
    }
    request = Request(scope)
    seen = {}

    async def call_next(_request):
        seen["request_id"] = get_request_id()
        return Response("ok")

    response = await request_id_middleware(request, call_next)

    assert response.headers.get("X-Request-Id") == "req-123"
    assert seen["request_id"] == "req-123"
    assert get_request_id() == "-"


@pytest.mark.asyncio
async def test_request_id_middleware_generates_id() -> None:
    """
    Middleware should generate a request id when missing.
    """
    scope = {
        "type": "http",
        "headers": [],
    }
    request = Request(scope)
    seen = {}

    async def call_next(_request):
        seen["request_id"] = get_request_id()
        return Response("ok")

    response = await request_id_middleware(request, call_next)

    response_id = response.headers.get("X-Request-Id")
    assert response_id
    assert response_id == seen["request_id"]
    assert get_request_id() == "-"
