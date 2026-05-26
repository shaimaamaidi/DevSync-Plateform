"""
Unit tests for CommitTaskMappingContainer.
"""

from unittest.mock import MagicMock

from backend.src.application.use_cases.map_commit_task_use_case import MapCommitTaskUseCase
from backend.src.infrastructure.di import commit_task_mapping_container
from backend.src.infrastructure.di.commit_task_mapping_container import CommitTaskMappingContainer


def _patch_base_containers(monkeypatch) -> None:
    """
    Patch base containers to avoid constructing external services.
    """
    def fake_ai_init(self) -> None:
        self.prompt_loader = MagicMock(name="prompt_loader")

    def fake_clickup_init(self) -> None:
        self.http_client = MagicMock(name="http_client")
        self.clickup_reader = MagicMock(name="clickup_reader")
        self.clickup_writer = MagicMock(name="clickup_writer")

    monkeypatch.setattr(commit_task_mapping_container.BaseAIContainer, "__init__", fake_ai_init)
    monkeypatch.setattr(commit_task_mapping_container.BaseClickUpContainer, "__init__", fake_clickup_init)


def test_commit_task_mapping_container_initializes_use_case(monkeypatch) -> None:
    """
    Test that the container wires the commit-task mapper and use case.
    """
    _patch_base_containers(monkeypatch)

    mapper_agent = MagicMock(name="mapper_agent")
    monkeypatch.setattr(commit_task_mapping_container, "CommitTaskMapperAgent", lambda prompt_loader: mapper_agent)

    container = CommitTaskMappingContainer()

    assert isinstance(container.commit_task_mapping_use_case, MapCommitTaskUseCase)
    assert container.commit_task_mapper_agent is mapper_agent
