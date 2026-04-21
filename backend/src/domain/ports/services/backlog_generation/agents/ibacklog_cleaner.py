"""
Service port for backlog cleaning operations.

This module defines the IBacklogCleaner interface, which specifies operations for
validating, normalizing, or cleaning a generated backlog structure before further processing
or persistence.
"""

from abc import abstractmethod, ABC

from backend.src.domain.entities.backlog.backlog_structure import BacklogStructure


class IBacklogCleaner(ABC):
    """
    Define backlog cleaning behavior required by the application.

    This interface is responsible for ensuring that a generated backlog is consistent,
    well-structured, and free of invalid or incomplete data before being used in downstream
    processes such as sprint planning or persistence.
    """

    @abstractmethod
    def clean_backlog(self, backlog: BacklogStructure) -> BacklogStructure:
        """
        Clean and normalize a backlog structure.

        This method applies validation and correction rules to ensure the backlog
        is consistent and properly structured.

        Args:
            backlog (BacklogStructure): The raw backlog structure to clean.

        Returns:
            BacklogStructure: The cleaned and normalized backlog structure.
        """
        pass