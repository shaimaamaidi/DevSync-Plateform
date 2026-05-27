"""
Unit tests for ProjectStatusContainer.
"""

from unittest.mock import MagicMock

from backend.src.infrastructure.di import project_status_container
from backend.src.infrastructure.di.project_status_container import ProjectStatusContainer


def _patch_base_containers(monkeypatch) -> None:
    """
    Patch base container initialization to avoid constructing real services.
    """
    def fake_ai_init(self) -> None:
        self.prompt_loader = MagicMock(name="prompt_loader")

    def fake_clickup_init(self) -> None:
        self.http_client = MagicMock(name="http_client")
        self.clickup_reader = MagicMock(name="clickup_reader")
        self.clickup_writer = MagicMock(name="clickup_writer")

    def fake_github_init(self) -> None:
        self.github_deployment_service = MagicMock(name="github_deployment_service")
        self.github_commit_service = MagicMock(name="github_commit_service")

    monkeypatch.setattr(project_status_container.BaseAIContainer, "__init__", fake_ai_init)
    monkeypatch.setattr(project_status_container.BaseClickUpContainer, "__init__", fake_clickup_init)
    monkeypatch.setattr(project_status_container.BaseGitHubContainer, "__init__", fake_github_init)


def _patch_dependencies(monkeypatch) -> dict[str, MagicMock]:
    """
    Patch project status dependencies with lightweight mocks.
    """
    mocks = {
        "stale_task_inspector": MagicMock(name="stale_task_inspector"),
        "unverified_done_task_inspector": MagicMock(name="unverified_done_task_inspector"),
        "project_status_use_case": MagicMock(name="project_status_use_case"),
    }

    monkeypatch.setattr(project_status_container, "StaleTaskInspectorAgent", lambda prompt_loader: mocks["stale_task_inspector"])
    monkeypatch.setattr(project_status_container, "UnverifiedDoneTaskInspectorAgent", lambda prompt_loader: mocks["unverified_done_task_inspector"])
    monkeypatch.setattr(project_status_container, "CheckProjectStatusUseCase", lambda *args, **kwargs: mocks["project_status_use_case"])

    return mocks


def test_project_status_container_initializes_use_case_and_agents(monkeypatch) -> None:
    """
    Test that the project status container wires its agents and use case.
    """
    _patch_base_containers(monkeypatch)
    mocks = _patch_dependencies(monkeypatch)

    container = ProjectStatusContainer()

    assert container.stale_task_inspector_agent is mocks["stale_task_inspector"]
    assert container.unverified_done_task_inspector_agent is mocks["unverified_done_task_inspector"]
    assert container.project_status_check_use_case is mocks["project_status_use_case"]
