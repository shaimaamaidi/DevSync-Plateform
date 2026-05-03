"""
Service port for sprint planning generation.

This module defines the ISprintPlanner interface, which specifies operations for transforming
a structured backlog into a sprint planning plan organized into iterative delivery cycles.
"""

from abc import ABC, abstractmethod

from backend.src.domain.entities.backlog.structure import BacklogStructure
from backend.src.domain.entities.sprint.planning import SprintPlanning


class ISprintPlanner(ABC):
    """
    Define sprint planning generation behavior required by the application.

    This interface is responsible for converting a backlog structure into a sprint planning
    representation by grouping and organizing work into sprints based on estimation, priority,
    and delivery constraints.
    """

    @abstractmethod
    def generate_sprints(self, backlog: BacklogStructure) -> SprintPlanning:
        """
        Generate sprint planning from a backlog structure.

        Args:
            backlog (BacklogStructure): Structured backlog containing epics, user stories, and tasks.

        Returns:
            SprintPlanning: Generated sprint plan with organized sprints and workload distribution.
        """
        pass