"""
Service port for saving verified backlog tasks.

This module defines the ISaveBacklogTaskInClickUpUseCase interface, which specifies
the operation for applying verified backlog task results into ClickUp.

It acts as a contract for application-level services responsible for:
- Applying task creation and update operations
- Resolving workspace members and assignees
- Synchronizing verified domain results with ClickUp
"""

from abc import ABC, abstractmethod
from typing import List

from backend.src.domain.entities.verified_tasks.verified_task_from_backlog import VerifiedTaskFromBacklog


class ISaveBacklogTasksInClickUpUseCase(ABC):
    """
    Define ClickUp task persistence behavior required by the application.

    This interface represents the contract for applying verified task results
    into ClickUp, abstracting external ClickUp API operations and member
    resolution logic.
    """

    @abstractmethod
    def save_backlog_tasks_to_clickup(
            self,
            tasks: List[VerifiedTaskFromBacklog],
            space_id,
            ignore_names: bool,
            ignore_mails: bool
    ) -> None:
        """
        Apply verified backlog tasks into ClickUp.

        Args:
            tasks (List[VerifiedTaskFromBacklog]): List of verified backlog task actions.
            space_id (str): ClickUp space identifier.
            ignore_names (bool): Whether to ignore name-based resolution.
            ignore_mails (bool): Whether to ignore email-based assignment.

        Returns:
            None
        """
        pass