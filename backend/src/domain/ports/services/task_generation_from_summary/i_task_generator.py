"""
Service port for task generation via LLMs.

This module defines the ITaskGenerator interface, which specifies operations for
generating tasks from a meeting summary using LLMs or external services.
"""

from abc import ABC, abstractmethod
from typing import List, Dict

from backend.src.domain.entities.generate_tasks_from_summary.generated_task import GeneratedTask


class ITaskGenerator(ABC):
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
        folders_statuses: Dict[str, Dict[str, List[str]]]
    ) -> List[GeneratedTask]:
        """
        Generate tasks from a meeting summary.

        Args:
            meeting_summary: Meeting summary in Arabic or French.
            folders_statuses: Mapping of folder names to their available
                statuses and priorities.

        Returns:
            List of GeneratedTask: Generated task objects.
        """
        pass