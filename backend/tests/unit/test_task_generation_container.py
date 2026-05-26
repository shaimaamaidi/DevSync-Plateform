"""
Unit tests for TaskGenerationContainer.
"""

from unittest.mock import MagicMock

import pytest

from backend.src.application.use_cases.generate_tasks_from_backlog_use_case import GenerateTasksFromBacklogUseCase
from backend.src.application.use_cases.generate_tasks_from_summary_use_case import GenerateTasksFromSummaryUseCase
from backend.src.application.use_cases.verify_tasks_from_backlog_use_case import VerifyTasksFromBacklogUseCase
from backend.src.application.use_cases.verify_tasks_from_summary_use_case import VerifyTasksFromSummaryUseCase
from backend.src.domain.exceptions.system.service_unavailable_exception import ServiceUnavailableException
from backend.src.infrastructure.di import task_generation_container
from backend.src.infrastructure.di.task_generation_container import TaskGenerationContainer


def _patch_base_containers(monkeypatch) -> None:
    """
    Patch base container initialization to avoid constructing real external services.
    """
    def fake_ai_init(self) -> None:
        self.prompt_loader = MagicMock(name="prompt_loader")

    def fake_clickup_init(self) -> None:
        self.http_client = MagicMock(name="http_client")
        self.clickup_reader = MagicMock(name="clickup_reader")
        self.clickup_writer = MagicMock(name="clickup_writer")

    monkeypatch.setattr(task_generation_container.BaseAIContainer, "__init__", fake_ai_init)
    monkeypatch.setattr(task_generation_container.BaseClickUpContainer, "__init__", fake_clickup_init)


def test_task_generation_container_initializes_all_use_cases(monkeypatch) -> None:
    """
    Test that the task generation container wires summary, backlog, and verification use cases.
    """
    _patch_base_containers(monkeypatch)

    summary_agent = MagicMock(name="summary_agent")
    backlog_agent = MagicMock(name="backlog_agent")
    summary_verifier = MagicMock(name="summary_verifier")
    backlog_verifier = MagicMock(name="backlog_verifier")

    monkeypatch.setattr(task_generation_container, "ClickUpTaskFromSummaryGeneratorAgent", lambda prompt_loader: summary_agent)
    monkeypatch.setattr(task_generation_container, "ClickUpTaskGeneratorFromBacklogAgent", lambda prompt_loader: backlog_agent)
    monkeypatch.setattr(task_generation_container, "TaskFromSummaryVerifierAgent", lambda prompt_loader: summary_verifier)
    monkeypatch.setattr(task_generation_container, "TaskFromBacklogVerifierAgent", lambda prompt_loader: backlog_verifier)

    container = TaskGenerationContainer()

    assert isinstance(container.clickup_task_generator_from_summary_use_case, GenerateTasksFromSummaryUseCase)
    assert isinstance(container.clickup_task_generator_from_backlog_use_case, GenerateTasksFromBacklogUseCase)
    assert isinstance(container.task_from_summary_verifier_agent, MagicMock)
    assert isinstance(container.task_from_backlog_verifier_agent, MagicMock)
    assert container.clickup_task_generator_from_summary_agent is summary_agent
    assert container.clickup_task_generator_from_backlog_agent is backlog_agent
    assert container.task_from_summary_verifier_agent is summary_verifier
    assert container.task_from_backlog_verifier_agent is backlog_verifier


def test_task_generation_container_creates_summary_save_use_case(monkeypatch) -> None:
    """
    Test that the container creates the summary save use case when ClickUp services are available.
    """
    _patch_base_containers(monkeypatch)

    monkeypatch.setattr(task_generation_container, "ClickUpTaskFromSummaryGeneratorAgent", lambda prompt_loader: MagicMock())
    monkeypatch.setattr(task_generation_container, "ClickUpTaskGeneratorFromBacklogAgent", lambda prompt_loader: MagicMock())
    monkeypatch.setattr(task_generation_container, "TaskFromSummaryVerifierAgent", lambda prompt_loader: MagicMock())
    monkeypatch.setattr(task_generation_container, "TaskFromBacklogVerifierAgent", lambda prompt_loader: MagicMock())

    container = TaskGenerationContainer()
    member_repo = MagicMock()

    use_case = container.create_save_summary_tasks_use_case(member_repo)

    assert use_case is not None
    assert container.clickup_reader is not None
    assert container.clickup_writer is not None


def test_task_generation_container_raises_when_clickup_service_is_missing(monkeypatch) -> None:
    """
    Test that the container raises a service error when ClickUp infrastructure is unavailable.
    """
    _patch_base_containers(monkeypatch)

    monkeypatch.setattr(task_generation_container, "ClickUpTaskFromSummaryGeneratorAgent", lambda prompt_loader: MagicMock())
    monkeypatch.setattr(task_generation_container, "ClickUpTaskGeneratorFromBacklogAgent", lambda prompt_loader: MagicMock())
    monkeypatch.setattr(task_generation_container, "TaskFromSummaryVerifierAgent", lambda prompt_loader: MagicMock())
    monkeypatch.setattr(task_generation_container, "TaskFromBacklogVerifierAgent", lambda prompt_loader: MagicMock())

    container = TaskGenerationContainer()
    container.clickup_reader = None

    with pytest.raises(ServiceUnavailableException):
        container.create_save_summary_tasks_use_case(MagicMock())


def test_task_generation_container_raises_when_summary_verifier_is_missing(monkeypatch) -> None:
    """
    Test that the container raises a service error when the summary verifier is unavailable.
    """
    _patch_base_containers(monkeypatch)

    monkeypatch.setattr(task_generation_container, "ClickUpTaskFromSummaryGeneratorAgent", lambda prompt_loader: MagicMock())
    monkeypatch.setattr(task_generation_container, "ClickUpTaskGeneratorFromBacklogAgent", lambda prompt_loader: MagicMock())
    monkeypatch.setattr(task_generation_container, "TaskFromSummaryVerifierAgent", lambda prompt_loader: MagicMock())
    monkeypatch.setattr(task_generation_container, "TaskFromBacklogVerifierAgent", lambda prompt_loader: MagicMock())

    container = TaskGenerationContainer()
    container.task_from_summary_verifier_agent = None

    with pytest.raises(ServiceUnavailableException):
        container.create_tasks_from_summary_verification_use_case(MagicMock())