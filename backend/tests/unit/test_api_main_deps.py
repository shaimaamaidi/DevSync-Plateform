"""
Unit tests for FastAPI app assembly and dependencies.
"""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from backend.src.domain.exceptions.base.app_exception import AppException
from backend.src.domain.exceptions.system.service_unavailable_exception import ServiceUnavailableException
from backend.src.presentation.api import deps
from backend.src.presentation.api.main import create_app
from backend.src.presentation.api.routers import clickup_structure_metadata_router


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


def test_get_container_closes_session_on_error() -> None:
    """
    get_container should close the session even if container creation fails.
    """
    session = MagicMock()
    request = SimpleNamespace(
        app=SimpleNamespace(state=SimpleNamespace(db=SimpleNamespace(get_session=MagicMock(return_value=session)))),
        url=SimpleNamespace(path="/x"),
    )

    original_container = deps.Container

    class _BoomContainer:
        def __init__(self, _session):
            raise RuntimeError("boom")

    deps.Container = _BoomContainer
    try:
        gen = deps.get_container(request)
        with pytest.raises(RuntimeError):
            next(gen)
    finally:
        deps.Container = original_container

    session.close.assert_called_once()


def test_get_backlog_use_case_missing_raises() -> None:
    """
    get_backlog_use_case should raise when use case is not initialized.
    """
    request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(workflow_container=SimpleNamespace(generate_backlog_use_case=None))))

    with pytest.raises(ServiceUnavailableException):
        deps.get_backlog_use_case(request)


def test_get_backlog_use_case_returns_instance() -> None:
    """
    get_backlog_use_case should return use case when available.
    """
    use_case = object()
    request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(workflow_container=SimpleNamespace(generate_backlog_use_case=use_case))))

    result = deps.get_backlog_use_case(request)

    assert result is use_case


def test_get_verify_task_use_case_missing_raises() -> None:
    request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(workflow_container=SimpleNamespace(verify_tasks_use_case=None))))

    with pytest.raises(ServiceUnavailableException):
        deps.get_verify_task_use_case(request)


def test_get_generate_task_from_summary_use_case_returns_instance() -> None:
    use_case = object()
    request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(workflow_container=SimpleNamespace(clickup_task_generator_use_case=use_case))))

    result = deps.get_generate_task_from_summary_use_case(request)

    assert result is use_case


def test_get_clickup_structure_metadata_use_case_returns_instance() -> None:
    use_case = object()
    request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(workflow_container=SimpleNamespace(clickup_structure_metadata_use_case=use_case))))

    result = clickup_structure_metadata_router.get_clickup_structure_metadata_use_case(request)

    assert result is use_case


def test_get_clickup_structure_metadata_use_case_missing_raises() -> None:
    request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(workflow_container=SimpleNamespace(clickup_structure_metadata_use_case=None))))

    with pytest.raises(ServiceUnavailableException):
        clickup_structure_metadata_router.get_clickup_structure_metadata_use_case(request)


def test_get_clickup_structure_creation_use_case_returns_instance() -> None:
    use_case = object()
    workflow_container = SimpleNamespace(create_clickup_structure_creation_use_case=MagicMock(return_value=use_case))
    request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(workflow_container=workflow_container)))
    container = SimpleNamespace(clickup_repo=object())

    result = deps.get_clickup_structure_creation_use_case(request, container=container)

    assert result is use_case
    workflow_container.create_clickup_structure_creation_use_case.assert_called_once_with(clickup_repo=container.clickup_repo)


def test_get_clickup_structure_creation_use_case_wraps_unexpected_error() -> None:
    workflow_container = SimpleNamespace(create_clickup_structure_creation_use_case=MagicMock(side_effect=RuntimeError("fail")))
    request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(workflow_container=workflow_container)))
    container = SimpleNamespace(clickup_repo=object())

    with pytest.raises(ServiceUnavailableException):
        deps.get_clickup_structure_creation_use_case(request, container=container)


def test_get_save_task_use_case_returns_instance() -> None:
    use_case = object()
    container = SimpleNamespace(member_repo=object())
    workflow_container = SimpleNamespace(create_save_task_use_case=MagicMock(return_value=use_case))
    request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(workflow_container=workflow_container)))

    result = deps.get_save_task_use_case(request, container=container)

    assert result is use_case
    workflow_container.create_save_task_use_case.assert_called_once_with(member_repo=container.member_repo)


def test_get_save_task_use_case_wraps_unexpected_error() -> None:
    container = SimpleNamespace(member_repo=object())
    workflow_container = SimpleNamespace(create_save_task_use_case=MagicMock(side_effect=RuntimeError("fail")))
    request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(workflow_container=workflow_container)))

    with pytest.raises(ServiceUnavailableException):
        deps.get_save_task_use_case(request, container=container)
