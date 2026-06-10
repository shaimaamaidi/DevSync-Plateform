"""
Service port for generating ClickUp tasks from a sprint backlog.

This module defines the IGenerateTaskFromBacklogUseCase interface, which specifies
the operation for transforming a sprint backlog into structured
ClickUp tasks.

It acts as a contract for application-level services responsible for:
- Parsing backlog
- Extracting actionable tasks
- Mapping tasks into ClickUp-compatible structures
"""

from abc import ABC, abstractmethod
from typing import List

from backend.src.domain.entities.generated_tasks.generated_task_from_backlog import GeneratedTaskFromBacklog
from backend.src.domain.entities.sprint.sprint import Sprint


class IGenerateTasksFromBacklogUseCase(ABC):
    """
    Define task generation behavior required by the application.

    This interface represents the contract for converting sprint backlogs
    into structured ClickUp tasks, abstracting the underlying generation logic
    (LLM, rules, or hybrid approaches).
    """

    @abstractmethod
    async def generate_tasks_from_backlog(self, sprint_backlog: List[Sprint], space_id) -> List[GeneratedTaskFromBacklog]:
        """
        Generate ClickUp tasks from a sprint backlog.

        Args:
            sprint_backlog (List[Sprint]): sprint backlog content.
            space_id (str): ClickUp space identifier.

        Returns:
            List[GeneratedTaskFromBacklog]: List of generated tasks.
        """
        pass