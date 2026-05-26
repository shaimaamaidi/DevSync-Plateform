"""
Service port for verifying generated ClickUp tasks.

This module defines the IVerifyTaskUseCase interface, which specifies
the operation for comparing generated tasks against existing ClickUp tasks
and producing a set of actions (create or update).

It acts as a contract for application-level services responsible for:
- Comparing generated tasks with existing ClickUp tasks
- Detecting changes based on task description matching
- Producing a diff of actions to apply in ClickUp
"""

from abc import ABC, abstractmethod
from typing import List

from backend.src.domain.entities.generated_tasks.generated_task_from_summary import GeneratedTaskFromSummary
from backend.src.domain.entities.verified_tasks.verified_task_from_summary import VerifiedTaskFromSummary


class IVerifyTasksFromSummaryUseCase(ABC):
    """
    Define ClickUp task verification behavior required by the application.

    This interface represents the contract for validating generated tasks
    against existing ClickUp tasks and producing only necessary changes
    (create or update operations), abstracting comparison logic and rules.
    """

    @abstractmethod
    def verify_tasks(
        self,
        tasks: List[GeneratedTaskFromSummary],
        space_id: str,
    ) -> List[VerifiedTaskFromSummary]:
        """
        Verify generated tasks against existing ClickUp tasks.

        Args:
            tasks (List[GeneratedTaskFromSummary]): List of generated tasks from summary to verify.
            space_id (str): ClickUp space identifier.

        Returns:
            List[VerifiedTaskFromSummary]: List of actions to apply (create or update only).
        """
        pass