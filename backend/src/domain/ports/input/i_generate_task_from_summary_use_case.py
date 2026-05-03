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

from typing import List

from backend.src.domain.entities.generate_tasks_from_summary.generated_task import GeneratedTask


class IGenerateTaskFromSummaryUseCase:
    """
    Define task generation behavior required by the application.

    This interface represents the contract for converting meeting summaries
    into structured ClickUp tasks, abstracting the underlying generation logic
    (LLM, rules, or hybrid approaches).
    """

    def generate_tasks_from_meeting_summary(self, meeting_summary: str, space_id) -> List[GeneratedTask]:
        """
        Generate ClickUp tasks from a meeting summary.

        Args:
            meeting_summary (str): Unstructured meeting summary text.
            space_id (str): ClickUp space identifier.

        Returns:
            List[GeneratedTask]: List of generated tasks.
        """
        pass