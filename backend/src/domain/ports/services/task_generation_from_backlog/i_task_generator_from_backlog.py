"""
Service port for task generation via LLMs.

This module defines the ITaskGeneratorFromBacklog interface, which specifies operations for
generating tasks from a backlog using LLMs or external services.
"""

from abc import ABC, abstractmethod
from typing import List, Dict

from backend.src.domain.entities.generated_tasks.generated_task_from_backlog import GeneratedTaskFromBacklog
from backend.src.domain.entities.sprint.sprint import Sprint


class ITaskGeneratorFromBacklog(ABC):
    """
    Define task generation behavior required by the application.

    This interface represents the contract for generating structured tasks
    from a backlog using an LLM or other external services.
    """

    @abstractmethod
    def generate_tasks(
        self,
        backlog: Sprint,
        locations_statuses: Dict[str, Dict[str, List[str]]]
    ) -> List[GeneratedTaskFromBacklog]:
        """
        Generate tasks from a backlog structure.

        Args:
            backlog: sprint backlog content.
            locations_statuses: Mapping of locations to their available statuses and priorities.

        Returns:
            List of GeneratedTaskFromBacklog: Generated task objects.
        """
        pass