"""
ClickUp workspace writer port for workspace structure management.

This module defines the IClickUpWorkSpaceWriter interface, which represents
the application contract for managing ClickUp workspace structure.

It specifies operations for creating and configuring workspace components such as:
- Spaces
- Folders
- Lists
- Custom statuses

This port is implemented by infrastructure adapters that translate domain-level
workspace structure decisions into ClickUp API operations.
"""

from abc import ABC, abstractmethod
from typing import Optional

from backend.src.domain.entities.clickup.list_metadata import ClickUpListMetadata
from backend.src.domain.entities.clickup.status import ClickUpStatus

class IClickUpWorkSpaceWriter(ABC):
    """
    Define ClickUp workspace writing behavior required by the application.

    This interface represents the contract for provisioning and updating
    ClickUp workspace structure based on domain-level configuration.
    """

    @abstractmethod
    def create_space(self, name: str) -> tuple[str, str]:
        """
        Create a new Space in the ClickUp workspace.

        Args:
            name: Name of the Space to create.

        Returns:
            tuple[str, str]: A tuple containing the created Space ID and name.
        """
        pass

    @abstractmethod
    def create_folder(self, space_id: str, name: str) -> tuple[str, str]:
        """
        Create a new Folder inside a Space.

        Args:
            space_id: The ClickUp Space ID.
            name: Name of the Folder to create.

        Returns:
            tuple[str, str]: A tuple containing the created folder ID and name.
        """
        pass

    @abstractmethod
    def create_list(
        self,
        space_id: str,
        name: str = "List",
        folder_id: Optional[str] = None,
    ) -> ClickUpListMetadata:
        """
        Create a new List in ClickUp.

        The list can be created inside a Folder or directly in a Space.

        Args:
            space_id: The ClickUp Space ID (used for folderless lists).
            name: Name of the List to create. Defaults to ``"List"``.
            folder_id: Optional Folder identifier.

        Returns:
            ClickUpListMetadata: A domain object representing the created List, including
                its ID, name, statuses, and priorities.
        """
        pass

    @abstractmethod
    def add_status_to_list(
            self,
            list_id: str,
            status: ClickUpStatus,
    ) -> ClickUpListMetadata:
        """
        Add a single status to an existing List without affecting other statuses.

        Fetches the current statuses from ClickUp, appends the new one,
        then sends a full replacement PUT request.

        Args:
            list_id: The ClickUp List ID to update.
            status: The new ClickUpStatus to add.

        Returns:
            ClickUpListMetadata: A domain object representing the created List, including
                it ID, name, priorities and the updated list of status names after adding
                the new status.
        """
        pass