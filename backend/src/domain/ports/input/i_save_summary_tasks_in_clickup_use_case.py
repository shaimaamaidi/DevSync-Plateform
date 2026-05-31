"""
Service port for saving verified summary tasks.

This module defines the ISaveSummaryTasksInClickUpUseCase interface, which specifies
the operation for applying verified summary task results into ClickUp.

It acts as a contract for application-level services responsible for:
- Applying task creation and update operations
- Resolving workspace members and assignees
- Synchronizing verified domain results with ClickUp
"""

from abc import ABC, abstractmethod
from typing import List

from backend.src.domain.entities.saved_tasks_request.task_sync_result import TaskSyncResult
from backend.src.domain.entities.verified_tasks.verified_task_from_summary import VerifiedTaskFromSummary


class ISaveSummaryTasksInClickUpUseCase(ABC):
    """
    Define ClickUp task persistence behavior required by the application.

    This interface represents the contract for applying verified summary task results
    into ClickUp, abstracting external ClickUp API operations and member
    resolution logic.
    """

    @abstractmethod
    def save_summary_tasks_to_clickup(
            self,
            tasks: List[VerifiedTaskFromSummary],
            space_id,
            ignore_names: bool,
            ignore_mails: bool
    ) -> TaskSyncResult:
        """
        Apply verified tasks into ClickUp.

        Args:
            tasks (List[VerifiedTaskFromSummary]): List of verified summary task actions.
            space_id (str): ClickUp space identifier.
            ignore_names (bool): Whether to ignore name-based resolution.
            ignore_mails (bool): Whether to ignore email-based assignment.

        Returns:
            TaskSyncResult: Summary of synchronization results, including created, updated,
                skipped, and failed tasks.
        """
        pass