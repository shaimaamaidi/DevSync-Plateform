"""
Integration tests for the FastAPI application factory.
"""

import sys
import types

from fastapi.middleware.cors import CORSMiddleware

_dummy_persistence = types.ModuleType("backend.src.infrastructure.di.persistence_container")
_dummy_persistence.PersistenceContainer = lambda session: None
_dummy_persistence.Container = _dummy_persistence.PersistenceContainer
sys.modules["backend.src.infrastructure.di.persistence_container"] = _dummy_persistence

from backend.src.infrastructure.handlers.exception_handler import FastAPIExceptionHandler
from backend.src.presentation.api import main
from backend.src.presentation.api.middleware.auth_middleware import JWTAuthMiddleware

if "backend.src.infrastructure.di.persistence_container" in sys.modules:
    del sys.modules["backend.src.infrastructure.di.persistence_container"]


def test_create_app_registers_core_routes_and_middlewares(monkeypatch) -> None:
    """
    Test that the app factory wires the main middleware, handlers, and routers.
    """
    monkeypatch.setattr(main, "setup_logger", lambda: None)

    app = main.create_app()

    assert app.title == "AI Backlog Generation & ClickUp Integration API"
    assert app.version == "1.0.0"
    assert JWTAuthMiddleware in [middleware.cls for middleware in app.user_middleware]
    assert CORSMiddleware in [middleware.cls for middleware in app.user_middleware]
    assert app.exception_handlers.get(Exception) is FastAPIExceptionHandler.handle_generic_exception
    assert app.exception_handlers.get(main.AppException) is FastAPIExceptionHandler.handle_app_exception
    assert app.exception_handlers.get(main.RequestValidationError) is FastAPIExceptionHandler.handle_validation_exception

    route_paths = {route.path for route in app.routes}

    assert "/health" in route_paths
    assert "/auth/login" in route_paths
    assert "/deployment/list" in route_paths
    assert "/repo/" in route_paths or "/repo" in route_paths