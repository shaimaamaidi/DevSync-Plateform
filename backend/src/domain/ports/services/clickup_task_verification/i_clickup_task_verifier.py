"""
Service port for verifying generated tasks.

This module defines the IClickUpTaskVerifier interface, which specifies
operations for verifying generated tasks against existing ClickUp tasks.
"""

from typing import List

from backend.src.domain.entities.clickup.clickup_list import ClickUpTask
from backend.src.domain.entities.clickup.generated_task import GeneratedTask
from backend.src.domain.entities.clickup.verified_task import VerifiedTask


class IClickUpTaskVerifier:
    """
    Define task verification behavior required by the application.

    This interface represents the contract for comparing generated tasks
    with existing ClickUp tasks in order to determine which tasks need
    to be created or updated.
    """

    def verify_tasks(
        self,
        existing_tasks: List[ClickUpTask],
        generated_tasks: List[GeneratedTask]
    ) -> List[VerifiedTask]:
        """
        Verify generated tasks against existing tasks.

        Args:
            existing_tasks: Tasks already present in ClickUp.
            generated_tasks: Tasks produced by the LLM.

        Returns:
            List of VerifiedTask: Tasks that require creation or update.
        """
        pass