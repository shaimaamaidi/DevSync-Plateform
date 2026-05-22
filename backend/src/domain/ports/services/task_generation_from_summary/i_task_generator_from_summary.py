"""
Service port for task generation via LLMs.

This module defines the ITaskGeneratorFromSummary interface, which specifies operations for
generating tasks from a meeting summary using LLMs or external services.
"""

from abc import ABC, abstractmethod
from typing import List, Dict

from backend.src.domain.entities.generated_tasks.generated_task_from_summary import GeneratedTaskFromSummary


class ITaskGeneratorFromSummary(ABC):
    """
    Define task generation behavior required by the application.

    This interface represents the contract for generating structured tasks
    from unstructured inputs (such as meeting summaries) using an LLM or
    other external services.
    """

    @abstractmethod
    def generate_tasks(
        self,
        meeting_summary: str,
        locations_statuses: Dict[str, Dict[str, List[str]]]
    ) -> List[GeneratedTaskFromSummary]:
        """
        Generate tasks from a meeting summary.

        Args:
            meeting_summary: Meeting summary in Arabic or French.
            locations_statuses: Mapping of locations to their available statuses and priorities.

        Returns:
            List of GeneratedTaskFromSummary: Generated task objects.
        """
        pass