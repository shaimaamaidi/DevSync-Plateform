"""
Service port for epic cleaning operations.

This module defines the IEpicCleaner interface, which specifies operations for
validating, normalizing, or cleaning a generated epic structure before further processing
or persistence.
"""

from abc import abstractmethod, ABC

from backend.src.domain.entities.backlog.structure import EpicBacklog


class IEpicCleaner(ABC):
    """
    Define epic cleaning behavior required by the application.

    This interface is responsible for ensuring that a generated epic is consistent,
    well-structured, and free of invalid or incomplete data before being used in downstream
    processes such as sprint planning or persistence.
    """

    @abstractmethod
    def clean_epic(self, epic: EpicBacklog) -> EpicBacklog:
        """
        Clean and normalize an epic structure.

        This method applies validation and correction rules to ensure the epic
        is consistent and properly structured.

        Args:
            epic (EpicBacklog): The raw epic structure to clean.

        Returns:
            EpicBacklog: The cleaned and normalized epic structure.
        """
        pass