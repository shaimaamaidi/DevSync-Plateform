"""
Unit tests for TaskStatusContainer.
"""

from unittest.mock import MagicMock

from backend.src.application.use_cases.task_status_check.search_task_use_case import SearchTaskUseCase
from backend.src.application.use_cases.task_status_check.synthesize_task_status_use_case import SynthesizeTaskStatusUseCase
from backend.src.infrastructure.di import task_status_container
from backend.src.infrastructure.di.task_status_container import TaskStatusContainer


def _patch_base_containers(monkeypatch) -> None:
    """
    Patch the base container initializers to avoid creating real external services.
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

    monkeypatch.setattr(task_status_container.BaseAIContainer, "__init__", fake_ai_init)
    monkeypatch.setattr(task_status_container.BaseClickUpContainer, "__init__", fake_clickup_init)
    monkeypatch.setattr(task_status_container.BaseGitHubContainer, "__init__", fake_github_init)


def test_task_status_container_initializes_use_cases(monkeypatch) -> None:
    """
    Test that the task status container wires the search and synthesis use cases.
    """
    _patch_base_containers(monkeypatch)

    search_agent = MagicMock(name="search_agent")
    synthesizer_agent = MagicMock(name="synthesizer_agent")
    monkeypatch.setattr(task_status_container, "TaskSearchAgent", lambda prompt_loader: search_agent)
    monkeypatch.setattr(task_status_container, "TaskStatusSynthesizerAgent", lambda prompt_loader: synthesizer_agent)

    container = TaskStatusContainer()

    assert isinstance(container.task_search_use_case, SearchTaskUseCase)
    assert isinstance(container.task_status_synthesize_use_case, SynthesizeTaskStatusUseCase)
    assert container.task_search_agent is search_agent
    assert container.task_status_synthesizer_agent is synthesizer_agent
