"""
Service port for mapping GitHub commits to ClickUp tasks.

This module defines the IMapCommitTaskUseCase interface, which specifies
the operation for associating a GitHub commit with its corresponding
ClickUp task inside a given space.

It acts as a contract for application-level services responsible for:
- Retrieving ClickUp task structures
- Performing semantic mapping between commits and tasks
- Ensuring traceability between development activity and task management
"""

from abc import ABC, abstractmethod
from typing import Optional

from backend.src.domain.entities.clickup.list_with_tasks import ClickUpTask
from backend.src.domain.entities.mapped_commit_task.mapped_commit_task_reponse import MappedCommitTaskResponse


class IMapCommitTaskUseCase(ABC):
    """
    Define commit-to-task mapping behavior required by the application.

    This interface represents the contract for resolving the relationship
    between a GitHub commit and a ClickUp task using domain-level logic
    and/or LLM-based semantic matching.
    """

    @abstractmethod
    def map_commit_task(self, commit: str, space_id: str) -> MappedCommitTaskResponse:
        """
        Map a GitHub commit to its corresponding ClickUp task.

        Args:
            commit (str): GitHub commit message or identifier.
            space_id (str): ClickUp space identifier.

        Returns:
            Optional[ClickUpTask]: The matched task if found, otherwise None.
        """
        pass