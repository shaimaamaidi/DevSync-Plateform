"""
Unit tests for FastAPI exception handler.
"""

import asyncio

from fastapi import Request

from backend.src.domain.exceptions.base.app_exception import AppException
from backend.src.domain.exceptions.repo.repo_not_found_exception import RepoNotFoundException
from backend.src.infrastructure.handlers.exception_handler import FastAPIExceptionHandler


def _make_request() -> Request:
    """
    Helper to create a minimal FastAPI Request object for testing.
    """
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/",
        "headers": [],
    }
    return Request(scope)


def test_handle_app_exception_returns_json() -> None:
    """
    Test that AppException is handled and returns a JSON response with status 400.
    """
    request = _make_request()
    exc = AppException("Boom")

    response = asyncio.run(FastAPIExceptionHandler.handle_app_exception(request, exc))

    assert response.status_code == 400
    assert response.body


def test_handle_app_exception_maps_not_found() -> None:
    """
    Test that RepoNotFoundException is handled and returns a JSON response with status 404.
    """
    request = _make_request()
    exc = RepoNotFoundException("Missing")

    response = asyncio.run(FastAPIExceptionHandler.handle_app_exception(request, exc))

    assert response.status_code == 404
    assert b"REPO_NOT_FOUND" in response.body
