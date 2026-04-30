"""
Service port for reading ClickUp structures and workspace data.

This module defines the IClickUpReader interface, which specifies operations for
retrieving ClickUp space structures (folders, lists) and workspace members.
"""

from abc import ABC, abstractmethod
from typing import List

from backend.src.domain.entities.clickup.folder import Folder


class IClickUpReader(ABC):
    """
    Define ClickUp reading behavior required by the application.

    This interface represents the contract for retrieving ClickUp data such as
    space structure (folders and lists) and workspace members.
    """

    @abstractmethod
    def get_space_structure(self, space_id: str) -> List[Folder]:
        """
        Fetch the full ClickUp space structure.

        This includes folders and their associated lists.

        Args:
            space_id: ClickUp space identifier.

        Returns:
            List[Folder]: List of folders representing the space structure.
        """
        pass

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