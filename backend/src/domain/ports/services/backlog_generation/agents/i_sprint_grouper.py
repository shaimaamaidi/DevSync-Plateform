"""
Service port for sprint grouping.

This module defines the ISprintGrouper interface, which specifies operations
for grouping user stories into coherent sprints and producing a structured
sprint planning output.
"""

from abc import ABC, abstractmethod

from backend.src.domain.entities.sprint.planning import SprintPlanning
from backend.src.domain.entities.sprint.sprint import UserStorySprint


class ISprintGrouper(ABC):
    """
    Define sprint grouping behavior required by the application.

    This interface is responsible for grouping estimated user stories into
    sprint-sized clusters and producing a structured SprintPlanning output.

    The grouping process is typically driven by:
    - Epic-level summaries
    - Estimated user stories
    - Sprint capacity / logical cohesion rules (optionally LLM-based)
    """

    @abstractmethod
    def group_sprints(
        self,
        epics: str,
        story_lookup: dict[str, UserStorySprint],
    ) -> SprintPlanning:
        """
        Group user stories into sprints and generate sprint planning.

        Args:
            epics (str): Serialized or summarized epics used as input context
                for sprint grouping.
            story_lookup (dict[str, UserStorySprint]): Mapping of story IDs
                to their estimated sprint-ready representations.

        Returns:
            SprintPlanning: Structured sprint plan containing grouped sprints
                and aggregated effort per sprint.
        """
        pass