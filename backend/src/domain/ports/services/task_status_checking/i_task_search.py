"""
Service port for task search via LLMs.

This module defines the ITaskSearchAgent interface, which specifies operations
for searching relevant tasks from ClickUp folders and lists using LLMs or
external services.
"""

from abc import ABC, abstractmethod
from typing import List

from backend.src.domain.entities.clickup.folder_with_lists import FolderWithLists
from backend.src.domain.entities.clickup.list_with_tasks import ClickUpTask


class ITaskSearch(ABC):
    """
    Define task search behavior required by the application.

    This interface represents the contract for searching and retrieving
    relevant ClickUp tasks based on a user question or query.
    """

    @abstractmethod
    def search_task(
        self,
        description: str,
        folder_with_tasks: List[FolderWithLists]
    ) -> List[ClickUpTask]:
        """
        Search for relevant tasks based on a user question.

        Args:
            description: User description or search request.
            folder_with_tasks: List of folders containing ClickUp lists and tasks.

        Returns:
            List of ClickUpTask: Tasks matching the search criteria.
        """
        pass