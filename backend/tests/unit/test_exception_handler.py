"""
Unit tests for FastAPI exception handlers.
"""

from types import SimpleNamespace
import json

import pytest

from backend.src.domain.exceptions.base.app_exception import AppException
from backend.src.infrastructure.handlers.exception_handler import FastAPIExceptionHandler


class _RequestWithPath:
    """
    Minimal request stub exposing a URL path.
    """

    def __init__(self, path: str) -> None:
        self.url = SimpleNamespace(path=path)


@pytest.mark.asyncio
async def test_handle_app_exception_maps_domain_error() -> None:
    """
    Test that handle_app_exception returns the expected error payload.
    """
    request = _RequestWithPath("/repo")
    exc = AppException("Repository not found", code="REPO_NOT_FOUND", http_status=404)

    response = await FastAPIExceptionHandler.handle_app_exception(request, exc)

    assert response.status_code == 404
    assert json.loads(response.body) == {
        "error": {
            "code": "REPO_NOT_FOUND",
            "message": "Repository not found",
        }
    }


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "code,message,http_status,expected_message",
    [
        ("INVALID_INPUT", "Bad input", 400, "Bad input"),
        ("PROMPT_FILE_NOT_FOUND", "Missing prompt", 500, "A server error occurred. Please try again later."),
        ("BACKLOG_GENERATION_ERROR", "Backlog failed", 500, "Backlog failed"),
        ("CLICKUP_API_ERROR", "ClickUp failed", 502, "ClickUp failed"),
        ("SOMETHING_ELSE", "Unexpected", 500, "Unexpected"),
    ],
)
async def test_handle_app_exception_maps_representative_code_groups(
    code: str,
    message: str,
    http_status: int,
    expected_message: str,
) -> None:
    """
    Test representative exception categories and message rewriting.
    """
    request = _RequestWithPath("/health")
    exc = AppException(message, code=code, http_status=http_status)

    response = await FastAPIExceptionHandler.handle_app_exception(request, exc)

    assert response.status_code == http_status
    assert json.loads(response.body) == {
        "error": {
            "code": code,
            "message": expected_message,
        }
    }


@pytest.mark.asyncio
async def test_handle_validation_exception_returns_validation_payload() -> None:
    """
    Test that handle_validation_exception returns validation details.
    """
    request = _RequestWithPath("/member")
    details = [{"loc": ["body", "mail"], "msg": "field required", "type": "value_error.missing"}]
    exc = SimpleNamespace(errors=lambda: details)

    response = await FastAPIExceptionHandler.handle_validation_exception(request, exc)

    assert response.status_code == 422
    assert json.loads(response.body) == {
        "error": {
            "code": "VALIDATION_ERROR",
            "message": "Request validation failed",
            "details": details,
        }
    }


@pytest.mark.asyncio
async def test_handle_generic_exception_returns_internal_server_error() -> None:
    """
    Test that handle_generic_exception hides unexpected errors.
    """
    request = _RequestWithPath("/deployment")

    response = await FastAPIExceptionHandler.handle_generic_exception(request, RuntimeError("boom"))

    assert response.status_code == 500
    assert json.loads(response.body) == {
        "error": {
            "code": "INTERNAL_SERVER_ERROR",
            "message": "Internal server error",
        }
    }
