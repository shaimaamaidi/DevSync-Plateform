"""
Use case port for ClickUp space structure metadata retrieval.

This module defines the IClickUpStructureMetadataUseCase interface, which specifies
operations for retrieving structural metadata of a ClickUp space such as folders
and their associated lists.

It acts as a contract for application-level use cases responsible for:
- Retrieving ClickUp space structure metadata
- Providing read-only access to folders and lists hierarchy
"""

from abc import ABC, abstractmethod
from typing import List

from backend.src.domain.entities.clickup.folder_with_list_metadata import FolderWithListsMetadata


class IClickUpStructureMetadataUseCase(ABC):
    """
    Define ClickUp space structure metadata retrieval behavior required by the application.

    This interface represents the contract for reading ClickUp workspace structure
    metadata, abstracting external ClickUp API access and infrastructure concerns.
    """

    @abstractmethod
    def get_space_structure_metadata(self, space_id: str) -> List[FolderWithListsMetadata]:
        """
        Retrieve metadata of a ClickUp space structure.

        This includes hierarchical information such as folders and lists
        belonging to the specified space.

        Args:
            space_id (str): ClickUp space identifier.

        Returns:
            List[FolderWithListsMetadata]: List of folders with their associated lists metadata.
        """
        pass