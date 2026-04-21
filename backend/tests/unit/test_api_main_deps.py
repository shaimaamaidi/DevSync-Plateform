"""
Unit tests for FastAPI app assembly and dependencies.
"""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI

from backend.src.domain.exceptions.system.service_unavailable_exception import ServiceUnavailableException
from backend.src.presentation.api import deps
from backend.src.presentation.api.main import create_app


def test_create_app_registers_routes() -> None:
    """
    create_app should include expected router prefixes.
    """
    app = create_app()
    paths = {route.path for route in app.router.routes}

    assert "/auth" in paths or any(p.startswith("/auth") for p in paths)
    assert "/clickup" in paths or any(p.startswith("/clickup") for p in paths)
    assert "/associate" in paths or any(p.startswith("/associate") for p in paths)
    assert "/repo" in paths or any(p.startswith("/repo") for p in paths)
    assert "/member" in paths or any(p.startswith("/member") for p in paths)
    assert "/deployment" in paths or any(p.startswith("/deployment") for p in paths)
    assert "/backlog" in paths or any(p.startswith("/backlog") for p in paths)


def test_get_container_closes_session() -> None:
    """
    get_container should close session after use.
    """
    session = MagicMock()
    request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(db=SimpleNamespace(get_session=MagicMock(return_value=session)))), url=SimpleNamespace(path="/x"))

    gen = deps.get_container(request)
    container = next(gen)
    assert container is not None

    gen.close()

    session.close.assert_called_once()


def test_get_backlog_use_case_missing_raises() -> None:
    """
    get_backlog_use_case should raise when use case is not initialized.
    """
    request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(backlog_container=SimpleNamespace(generate_backlog_use_case=None))))

    with pytest.raises(ServiceUnavailableException):
        deps.get_backlog_use_case(request)


def test_get_backlog_use_case_returns_instance() -> None:
    """
    get_backlog_use_case should return use case when available.
    """
    use_case = object()
    request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(backlog_container=SimpleNamespace(generate_backlog_use_case=use_case))))

    result = deps.get_backlog_use_case(request)

    assert result is use_case
