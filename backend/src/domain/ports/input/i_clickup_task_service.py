"""
Service port for ClickUp task and workspace structure management.

This module defines the IClickUpTaskService interface, which specifies operations
for retrieving ClickUp space structure, workspace members, and managing cached data.

It acts as a contract for application-level services responsible for:
- Retrieving ClickUp space hierarchy (folders, lists, tasks)
- Fetching workspace members
- Managing in-memory cache for performance optimization
"""

from typing import List

from backend.src.domain.entities.clickup.folder_with_lists import FolderWithLists


class IClickUpTaskService:
    """
    Define ClickUp task service behavior required by the application.

    This interface represents the contract for accessing ClickUp workspace
    structure and related metadata, abstracting external ClickUp API calls
    and caching mechanisms.
    """

    def get_space_structure(self, space_id: str) -> List[FolderWithLists]:
        """
        Retrieve ClickUp space structure.

        Args:
            space_id (str): ClickUp space identifier.

        Returns:
            List[FolderWithLists]: List of folders representing the space structure with lists9.
        """
        pass

    def get_workspace_members(self, space_id: str) -> List[dict]:
        """
        Retrieve workspace members for a ClickUp space.

        Args:
            space_id (str): ClickUp space identifier.

        Returns:
            List[dict]: List of workspace members with metadata.
        """
        pass

    def invalidate(self, space_id: str) -> None:
        """
        Invalidate cached space structure.

        This method clears cached data for the given space to ensure fresh
        retrieval on the next request.

        Args:
            space_id (str): ClickUp space identifier.
        """
        pass