"""
Service port for verifying tasks.

This module defines the ITaskFromSummaryVerifier interface, which specifies
operations for verifying tasks from a summary against existing ClickUp tasks
and return only tasks that need to create or update.
"""

from abc import ABC, abstractmethod
from typing import List

from backend.src.domain.entities.clickup.list_with_tasks import ClickUpTask
from backend.src.domain.entities.generated_tasks.generated_task_from_summary import GeneratedTaskFromSummary
from backend.src.domain.entities.verified_tasks.verified_task_from_summary import VerifiedTaskFromSummary


class ITaskFromSummaryVerifier(ABC):
    """
    Define task verification behavior required by the application.

    This interface represents the contract for comparing tasks generated
    from a summary with existing ClickUp tasks in order to determine which
    tasks need to be created or updated.
    """

    @abstractmethod
    def verify_tasks(
        self,
        existing_tasks: List[ClickUpTask],
        tasks: List[GeneratedTaskFromSummary]
    ) -> List[VerifiedTaskFromSummary]:
        """
        Verify tasks generated from a summary against existing tasks.

        Args:
            existing_tasks: Tasks already present in ClickUp.
            tasks: Tasks produced by the LLM.

        Returns:
            List of VerifiedTaskFromSummary: Tasks that require creation or update.
        """
        pass