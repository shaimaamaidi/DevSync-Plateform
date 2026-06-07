"""
Unit tests for ReadClickUpSpaceTaskUseCase.
"""

from unittest.mock import MagicMock

import pytest

from backend.src.application.use_cases.read_clickup_space_task_use_case import ReadClickUpSpaceTaskUseCase
from backend.src.domain.entities.clickup.folder_with_lists import FolderWithLists
from backend.src.domain.exceptions.common.invalid_input_exception import InvalidInputException


def test_get_tasks_by_space_calls_reader() -> None:
    """
    Test that the use case delegates task loading to the ClickUp reader.
    """
    clickup_reader = MagicMock()
    expected = [FolderWithLists(id="folder-1", name="Backend", lists=[])]
    clickup_reader.get_space_full_structure_with_estimation.return_value = expected
    use_case = ReadClickUpSpaceTaskUseCase(clickup_reader)

    result = use_case.get_tasks_by_space("space-1")

    assert result == expected
    clickup_reader.get_space_full_structure_with_estimation.assert_called_once_with("space-1")


def test_get_tasks_by_space_raises_for_empty_space_id() -> None:
    """
    Test that the use case rejects an empty space id.
    """
    use_case = ReadClickUpSpaceTaskUseCase(MagicMock())

    with pytest.raises(InvalidInputException):
        use_case.get_tasks_by_space("")