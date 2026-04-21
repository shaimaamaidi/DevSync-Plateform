"""
Service port for backlog prioritization.

This module defines the IBacklogPrioritizer interface, which specifies operations for
prioritizing elements within a backlog structure to improve delivery order and planning.
"""

from abc import ABC, abstractmethod

from backend.src.domain.entities.backlog.backlog_structure import BacklogStructure


class IBacklogPrioritizer(ABC):
    """
    Define backlog prioritization behavior required by the application.

    This interface is responsible for applying prioritization rules on a backlog structure
    in order to order epics, user stories, or tasks based on business value, dependencies,
    or strategic importance.
    """

    @abstractmethod
    def prioritize(self, backlog: BacklogStructure) -> BacklogStructure:
        """
        Prioritize a backlog structure.

        This method applies prioritization logic to reorder or adjust backlog elements
        according to business rules or scoring strategies.

        Args:
            backlog (BacklogStructure): The backlog structure to prioritize.

        Returns:
            BacklogStructure: The prioritized backlog structure.
        """
        pass