"""
Use case port for ClickUp space task retrieval.

This module defines the IClickUpSpaceTaskReaderUseCase interface, which specifies
operations for retrieving the complete task structure of a ClickUp space.

It acts as a contract for application-level use cases responsible for:
- Retrieving folders inside a ClickUp space
- Retrieving lists associated with folders
- Retrieving tasks associated with lists
"""

from abc import ABC, abstractmethod
from typing import List

from backend.src.domain.entities.clickup.folder_with_lists import FolderWithLists


class IReadClickUpSpaceTaskUseCase(ABC):
    """
    Define ClickUp space task retrieval behavior required by the application.

    This interface represents the contract for retrieving the hierarchical
    structure of a ClickUp space, including folders, lists, and tasks,
    while delegating infrastructure operations to external adapters.
    """

    @abstractmethod
    def get_tasks_by_space(self, space_id) -> List[FolderWithLists]:
        """
        Retrieve the complete task structure of a ClickUp space.

        Args:
            space_id (str): ClickUp space identifier.

        Returns:
            List[FolderWithLists]:
                List of folders containing their associated lists and tasks.
        """
        pass