"""
Service port for sprint planning generation.

This module defines the ISprintPlanner interface, which specifies operations
for transforming a structured backlog into a sprint planning representation
organized into iterative delivery cycles.
"""

from abc import ABC, abstractmethod

from backend.src.domain.entities.backlog.structure import BacklogStructure
from backend.src.domain.entities.sprint.planning import SprintPlanning


class ISprintPlanner(ABC):
    """
    Define sprint planning generation behavior required by the application.

    This interface is responsible for transforming a structured backlog into
    a complete sprint planning plan by:
    - Grouping work into sprints
    - Ensuring workload distribution across iterations
    - Respecting prioritization and estimation constraints
    - Supporting agile delivery planning

    It acts as the high-level orchestration contract for sprint planning systems.
    """

    @abstractmethod
    def plan_sprints(self, backlog: BacklogStructure) -> SprintPlanning:
        """
        Generate sprint planning from a structured backlog.

        This method transforms a backlog into a sprint-based delivery plan
        by organizing epics, user stories, and tasks into iterative sprints.

        Args:
            backlog (BacklogStructure): Structured backlog containing:
                - epics
                - user stories
                - tasks

        Returns:
            SprintPlanning: Final sprint plan containing:
                - grouped sprints
                - workload distribution
                - structured delivery iterations
        """
        pass