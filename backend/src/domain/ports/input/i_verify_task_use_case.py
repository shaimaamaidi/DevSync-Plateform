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

from typing import List

from backend.src.domain.entities.generate_tasks_from_summary.generated_task import GeneratedTask
from backend.src.domain.entities.verify_tasks.verified_task import VerifiedTask


class IVerifyTaskUseCase:
    """
    Define ClickUp task verification behavior required by the application.

    This interface represents the contract for validating generated tasks
    against existing ClickUp tasks and producing only necessary changes
    (create or update operations), abstracting comparison logic and rules.
    """

    def verify_tasks(self, tasks: List[GeneratedTask], space_id) -> List[VerifiedTask]:
        """
        Verify generated tasks against existing ClickUp tasks.

        Args:
            tasks (List[GeneratedTask]): List of generated tasks to verify.
            space_id (str): ClickUp space identifier.

        Returns:
            List[VerifiedTask]: List of actions to apply (create or update only).
        """
        pass