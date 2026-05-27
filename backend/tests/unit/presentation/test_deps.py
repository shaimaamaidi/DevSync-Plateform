"""
Unit tests for FastAPI dependency providers.
"""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from backend.src.domain.exceptions.system.service_unavailable_exception import ServiceUnavailableException
from backend.src.presentation.api import deps


def _make_request(path: str = "/repo"):
    """
    Build a minimal request stub for dependency tests.
    """
    return SimpleNamespace(
        url=SimpleNamespace(path=path),
        app=SimpleNamespace(state=SimpleNamespace()),
    )


def test_get_persistence_container_yields_container_and_closes_session(monkeypatch) -> None:
    """
    Test that the persistence container is created from the DB session and closed afterward.
    """
    request = _make_request()
    session = MagicMock()
    request.app.state.db = SimpleNamespace(get_session=MagicMock(return_value=session))

    class DummyPersistenceContainer:
        """
        Minimal persistence container stub.
        """

        def __init__(self, session) -> None:
            self.session = session

    monkeypatch.setattr(deps, "PersistenceContainer", DummyPersistenceContainer)

    generator = deps.get_persistence_container(request)
    container = next(generator)

    assert isinstance(container, DummyPersistenceContainer)
    assert container.session is session

    generator.close()

    request.app.state.db.get_session.assert_called_once()
    session.close.assert_called_once()


def test_get_generate_backlog_use_case_returns_container_value() -> None:
    """
    Test that the backlog use case is read from the application container.
    """
    request = _make_request("/backlog")
    use_case = MagicMock()
    request.app.state.backlog_generation_container = SimpleNamespace(generate_backlog_use_case=use_case)

    result = deps.get_generate_backlog_use_case(request)

    assert result is use_case


def test_get_generate_backlog_use_case_raises_when_unavailable() -> None:
    """
    Test that the backlog provider raises a service error when the use case is missing.
    """
    request = _make_request("/backlog")
    request.app.state.backlog_generation_container = SimpleNamespace(generate_backlog_use_case=None)

    with pytest.raises(ServiceUnavailableException):
        deps.get_generate_backlog_use_case(request)


def test_get_generate_task_from_backlog_use_case_returns_container_value() -> None:
    """
    Test that the backlog task generation use case is read from the application container.
    """
    request = _make_request("/clickup/tasks")
    use_case = MagicMock()
    request.app.state.task_generation_container = SimpleNamespace(
        clickup_task_generator_from_backlog_use_case=use_case,
    )

    result = deps.get_generate_task_from_backlog_use_case(request)

    assert result is use_case


def test_get_deployment_use_case_wires_repo_dependency() -> None:
    """
    Test that the deployment use case is created with the request-scoped repository.
    """
    request = _make_request("/deployment")
    repo_repo = MagicMock()
    expected_use_case = MagicMock()
    request.app.state.deployment_container = SimpleNamespace(create_deployment_use_case=MagicMock(return_value=expected_use_case))

    result = deps.get_deployment_use_case(request, container=SimpleNamespace(repo_repo=repo_repo))

    assert result is expected_use_case
    request.app.state.deployment_container.create_deployment_use_case.assert_called_once_with(repo_repo)


def test_get_save_summary_tasks_use_case_wires_member_repo() -> None:
    """
    Test that the summary save use case receives the member repository.
    """
    request = _make_request("/clickup/tasks")
    member_repo = MagicMock()
    expected_use_case = MagicMock()
    request.app.state.task_generation_container = SimpleNamespace(
        create_save_summary_tasks_use_case=MagicMock(return_value=expected_use_case)
    )

    result = deps.get_save_summary_tasks_use_case(request, container=SimpleNamespace(member_repo=member_repo))

    assert result is expected_use_case
    request.app.state.task_generation_container.create_save_summary_tasks_use_case.assert_called_once_with(
        member_repo=member_repo
    )


def test_get_create_clickup_structure_use_case_wires_both_repositories() -> None:
    """
    Test that the ClickUp structure use case receives both repositories.
    """
    request = _make_request("/clickup/structure")
    clickup_repo = MagicMock()
    member_repo = MagicMock()
    expected_use_case = MagicMock()
    request.app.state.clickup_container = SimpleNamespace(
        create_clickup_structure_creation_use_case=MagicMock(return_value=expected_use_case)
    )

    result = deps.get_create_clickup_structure_use_case(
        request,
        container=SimpleNamespace(clickup_repo=clickup_repo, member_repo=member_repo),
    )

    assert result is expected_use_case
    request.app.state.clickup_container.create_clickup_structure_creation_use_case.assert_called_once_with(
        clickup_repo=clickup_repo,
        member_repo=member_repo,
    )