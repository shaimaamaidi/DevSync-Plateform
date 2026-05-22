"""
Service port for verifying tasks.

This module defines the IClickUpTaskVerifier interface, which specifies
operations for verifying tasks against existing ClickUp tasks and return
only tasks who need to create or update.
"""

from abc import ABC, abstractmethod
from typing import List

from backend.src.domain.entities.clickup.list_with_tasks import ClickUpTask
from backend.src.domain.entities.generated_tasks.generated_task_from_summary import GeneratedTaskFromSummary
from backend.src.domain.entities.verify_tasks.verified_task import VerifiedTask


class IClickUpTaskVerifier(ABC):
    """
    Define task verification behavior required by the application.

    This interface represents the contract for comparing tasks
    with existing ClickUp tasks in order to determine which tasks need
    to be created or updated.
    """

    @abstractmethod
    def verify_tasks(
        self,
        existing_tasks: List[ClickUpTask],
        tasks: List[GeneratedTaskFromSummary]
    ) -> List[VerifiedTask]:
        """
        Verify tasks against existing tasks.

        Args:
            existing_tasks: Tasks already present in ClickUp.
            tasks: Tasks produced by the LLM.

        Returns:
            List of VerifiedTask: Tasks that require creation or update.
        """
        pass