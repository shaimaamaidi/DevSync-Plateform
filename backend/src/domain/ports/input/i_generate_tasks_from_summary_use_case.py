"""
Service port for generating ClickUp tasks from a meeting summary.

This module defines the IGenerateTaskFromSummaryUseCase interface, which specifies
the operation for transforming an unstructured meeting summary into structured
ClickUp tasks.

It acts as a contract for application-level services responsible for:
- Parsing meeting summaries
- Extracting actionable tasks
- Mapping tasks into ClickUp-compatible structures
"""

from abc import ABC, abstractmethod
from typing import List

from backend.src.domain.entities.generated_tasks.generated_task_from_summary import GeneratedTaskFromSummary


class IGenerateTasksFromSummaryUseCase(ABC):
    """
    Define task generation behavior required by the application.

    This interface represents the contract for converting meeting summaries
    into structured ClickUp tasks, abstracting the underlying generation logic
    (LLM, rules, or hybrid approaches).
    """

    @abstractmethod
    def generate_tasks_from_meeting_summary(self, meeting_summary: str, space_id) -> List[GeneratedTaskFromSummary]:
        """
        Generate ClickUp tasks from a meeting summary.

        Args:
            meeting_summary (str): Unstructured meeting summary text.
            space_id (str): ClickUp space identifier.

        Returns:
            List[GeneratedTaskFromSummary]: List of generated tasks.
        """
        pass