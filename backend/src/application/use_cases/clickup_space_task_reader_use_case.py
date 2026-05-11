"""
ClickUp space task reader use case module.

This module provides the ClickUpSpaceTaskReaderUseCase class, which is responsible
for retrieving the complete task structure of a ClickUp space.

The use case exposes read-only operations for accessing folders, lists,
and their associated tasks from ClickUp by delegating retrieval to the
ClickUpReader port.

It does not apply business mutations, synchronization logic, or caching.

Classes:
    ClickUpSpaceTaskReaderUseCase:
        Use case for retrieving folders, lists, and tasks from a ClickUp space.
"""

import logging
from typing import List

from backend.src.domain.entities.clickup.folder_with_lists import FolderWithLists
from backend.src.domain.ports.input.i_clickup_space_task_reader_use_case import IClickUpSpaceTaskReaderUseCase
from backend.src.domain.ports.output.clickup.i_clickup_reader import IClickUpReader


logger = logging.getLogger(__name__)


class ClickUpSpaceTaskReaderUseCase(IClickUpSpaceTaskReaderUseCase):
    """
    Application use case for retrieving ClickUp space tasks.

    This class provides read-only access to the complete structure
    of a ClickUp space, including folders, lists, and their associated
    tasks.

    Retrieval operations are delegated to the ClickUpReader port
    without applying caching or business modification logic.

    Attributes:
        _clickup_reader (IClickUpReader):
            Port used to retrieve data from the ClickUp API.
    """

    def __init__(self, clickup_reader: IClickUpReader):
        """
        Initialize the use case with a ClickUp reader port.

        Args:
            clickup_reader (IClickUpReader): ClickUp reader port implementation.
        """
        self._clickup_reader = clickup_reader

    def get_tasks_by_space(self, space_id) -> List[FolderWithLists]:
        """
        Retrieve the complete task structure of a ClickUp space.

        This method fetches folders, lists, and their associated tasks
        for the specified ClickUp space by delegating retrieval to the
        ClickUp reader port.

        Args:
            space_id (str): ClickUp space identifier.

        Returns:
            List[FolderWithLists]: List of folders containing their associated lists and tasks.
        """
        logger.info(
            "Fetching ClickUp tasks by space. space_id=%s.",
            space_id,
        )

        results = self._clickup_reader.get_space_full_structure(space_id)

        logger.info(
            "ClickUp tasks fetched successfully. space_id=%s folders=%d.",
            space_id,
            len(results),
        )

        return results
