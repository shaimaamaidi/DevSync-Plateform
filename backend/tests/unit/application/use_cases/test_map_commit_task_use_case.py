"""
Unit tests for MapCommitTaskUseCase.
"""

from types import SimpleNamespace
import asyncio
from unittest.mock import MagicMock

from backend.src.application.use_cases.map_commit_task_use_case import MapCommitTaskUseCase
from backend.src.domain.entities.clickup.list_with_tasks import ClickUpTask
from backend.src.domain.entities.mapped_commit_task.mapped_commit_task_reponse import CommitTaskMappingStatus


def test_map_commit_task_returns_empty_status_when_space_has_no_tasks() -> None:
    """
    Test that mapping returns the empty-space response when no tasks exist.
    """
    clickup_reader = MagicMock()
    clickup_reader.get_space_full_structure.return_value = [
        SimpleNamespace(id="folder-1", lists=[SimpleNamespace(tasks=[])])
    ]
    mapper = MagicMock()

    use_case = MapCommitTaskUseCase(clickup_reader, mapper)

    result = asyncio.run(use_case.map_commit_task("commit-1", "space-1"))

    assert result.status == CommitTaskMappingStatus.CLICK_UP_EMPTY
    assert result.task is None
    mapper.map_commit_task.assert_not_called()


def test_map_commit_task_returns_found_response() -> None:
    """
    Test that mapping returns a found response when the mapper matches a task.
    """
    task = ClickUpTask(id="task-1", name="Task 1", description=None, status=None, assignee=None, priority=None)
    object.__setattr__(task, "task_id", "task-1")
    clickup_reader = MagicMock()
    clickup_reader.get_space_full_structure.return_value = [
        SimpleNamespace(id="folder-1", lists=[SimpleNamespace(tasks=[task])])
    ]
    mapper = MagicMock()
    mapper.map_commit_task.return_value = task

    use_case = MapCommitTaskUseCase(clickup_reader, mapper)

    # Patch async filter to return the eligible tasks immediately
    import backend.src.application.use_cases.map_commit_task_use_case as mapmod

    async def fake_filter(_reader, _tasks):
        return [task]

    mapmod.filter_search_candidates = fake_filter

    result = asyncio.run(use_case.map_commit_task("commit-1", "space-1"))

    assert result.status == CommitTaskMappingStatus.FOUND
    assert result.task == task
    mapper.map_commit_task.assert_called_once_with("commit-1", [task])
