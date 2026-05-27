"""
Unit tests for ClickUpContainer.
"""

from unittest.mock import MagicMock

from backend.src.infrastructure.di import clickup_container
from backend.src.infrastructure.di.clickup_container import ClickUpContainer


def _patch_base_container(monkeypatch) -> None:
    """
    Patch base ClickUp initialization to avoid real network setup.
    """
    def fake_init(self) -> None:
        self.http_client = MagicMock(name="http_client")
        self.clickup_reader = MagicMock(name="clickup_reader")
        self.clickup_writer = MagicMock(name="clickup_writer")

    monkeypatch.setattr(clickup_container.BaseClickUpContainer, "__init__", fake_init)


def _patch_dependencies(monkeypatch) -> dict[str, MagicMock]:
    """
    Patch workflow dependencies with lightweight mocks.
    """
    mocks = {
        "workspace_writer": MagicMock(name="workspace_writer"),
        "structure_metadata": MagicMock(name="structure_metadata"),
        "space_task_reader": MagicMock(name="space_task_reader"),
        "task_manager": MagicMock(name="task_manager"),
        "structure_creation": MagicMock(name="structure_creation"),
    }

    monkeypatch.setattr(clickup_container, "ClickUpWorkSpaceWriter", lambda http_client: mocks["workspace_writer"])
    monkeypatch.setattr(clickup_container, "ClickUpStructureMetadataUseCase", lambda clickup_reader: mocks["structure_metadata"])
    monkeypatch.setattr(clickup_container, "ReadClickUpSpaceTaskUseCase", lambda clickup_reader: mocks["space_task_reader"])
    monkeypatch.setattr(clickup_container, "ManageClickUpTaskUseCase", lambda clickup_writer, clickup_reader: mocks["task_manager"])
    monkeypatch.setattr(clickup_container, "ManageClickUpStructureUseCase", lambda **kwargs: mocks["structure_creation"])

    return mocks


def test_clickup_container_initializes_use_cases_and_factories(monkeypatch) -> None:
    """
    Test that the ClickUp container wires use cases and workspace writer.
    """
    _patch_base_container(monkeypatch)
    mocks = _patch_dependencies(monkeypatch)

    container = ClickUpContainer()

    assert container.clickup_workspace_writer is mocks["workspace_writer"]
    assert container.clickup_structure_metadata_use_case is mocks["structure_metadata"]
    assert container.clickup_space_task_reader_use_case is mocks["space_task_reader"]
    assert container.clickup_task_creation_use_case is mocks["task_manager"]

    factory_result = container.create_clickup_structure_creation_use_case(MagicMock(), MagicMock())

    assert factory_result is mocks["structure_creation"]
