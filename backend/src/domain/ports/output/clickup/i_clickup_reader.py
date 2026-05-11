"""
Service port for reading ClickUp structures and workspace data.

This module defines the IClickUpReader interface, which specifies operations for
retrieving ClickUp space structures (folders, lists) and workspace members.
"""

from abc import ABC, abstractmethod
from typing import List

from backend.src.domain.entities.clickup.folder_with_list_metadata import FolderWithListsMetadata
from backend.src.domain.entities.clickup.folder_with_lists import FolderWithLists


class IClickUpReader(ABC):
    """
    Define ClickUp reading behavior required by the application.

    This interface represents the contract for retrieving ClickUp data such as
    space structure (folders and lists) and workspace members.
    """

    @abstractmethod
    def space_exists(self, space_code: str) -> str:
        """
        Check whether a ClickUp space exists and is accessible.

        Args:
            space_code: ClickUp space identifier in the click up.

        Returns:
            Space name if the space exists and is accessible.
        """
        pass

    @abstractmethod
    def get_space_full_structure(self, space_id: str) -> List[FolderWithLists]:
        """
        Fetch the full ClickUp space structure.

        This includes folders and their associated lists.

        Args:
            space_id: ClickUp space identifier.

        Returns:
            List[FolderWithLists]: List of folders representing the space structure.
        """
        pass

    @abstractmethod
    def get_space_structure_metadata(self, space_id: str) -> List[FolderWithListsMetadata]:
        """
        Retrieve ClickUp space structure (metadata only).

        Includes folders and lists with their configuration metadata
        (statuses and priorities), without retrieving tasks.

        Args:
            space_id: ClickUp space identifier.

        Returns:
            List of FolderWithListsMetadata containing lists metadata.
        """

    @abstractmethod
    def get_workspace_members(self, space_id: str) -> List[dict]:
        """
        Fetch workspace members for the current space.

        Args:
            space_id: ClickUp space identifier.

        Returns:
            List[dict]: List of workspace members with their metadata
            (e.g., id, username, email).
        """
        pass