"""
Service port for reading ClickUp structures and workspace data.

This module defines the IClickUpReader interface, which specifies operations for
retrieving ClickUp space structures (folders, lists) and workspace members.
"""

from abc import ABC, abstractmethod
from typing import List

from backend.src.domain.entities.clickup.folder_with_list_metadata import FolderWithListsMetadata
from backend.src.domain.entities.clickup.folder_with_lists import FolderWithLists
from backend.src.domain.entities.clickup.list_with_tasks import ClickUpTask


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
    def get_workspace_members(self) -> List[dict]:
        """
        Fetch workspace members for the current space.

        Returns:
            List[dict]: List of workspace members with their metadata
            (e.g., id, username, email).
        """
        pass

    @abstractmethod
    def get_workspace_members_with_roles(self) -> List[dict]:
        """
        Retrieve ClickUp workspace members with their roles from the first available team.

        Returns:
            List of member dicts with keys: id, email, role.

        Raises:
            ClickUpWorkspaceMembersException: If no valid members are found.
        """
        pass

    @abstractmethod
    def get_task_by_id(self, task_id: str) -> ClickUpTask:
        """
        Retrieve a single task by its ID.

        Args:
            task_id: ClickUp task identifier.

        Returns:
            ClickUpTask: Parsed task dict with status, assignees, dates, and description.

        Raises:
            ClickUpResourceNotFoundException: If the task does not exist.
        """
        pass

    @abstractmethod
    def get_task_time_context(self, task_id: str) -> dict:
        """
        Retrieve all available date signals for a task.

        ClickUp does not expose a full status-change history via API.
        This method collects every date signal available and derives
        `since_current_status` from time_in_status when possible.

        Collected signals:
            - date_created : when the task was created (exact)
            - date_updated : last modification of any field (exact)
            - date_closed : when marked Done/Closed (exact, or None)
            - start_date : manually set start date (or None)
            - due_date : due date if set (or None)
            - current_status : current status string
            - since_current_status : datetime when task entered current status
                derived from time_in_status.current_status.since
                (requires "Total time in Status" ClickApp enabled)

        Args:
            task_id: ClickUp task identifier.

        Returns:
            Dict with keys:
                date_created (datetime)
                date_updated (datetime)
                date_closed (datetime | None)
                start_date (datetime | None)
                due_date (datetime | None)
                current_status (str)
                since_current_status (datetime | None)
        """
        pass