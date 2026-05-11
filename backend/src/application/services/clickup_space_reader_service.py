"""
ClickUp task service module.

This module provides the ClickUpTaskService class, which manages ClickUp-related
operations such as retrieving space structure and workspace members.

Classes:
    ClickUpTaskService: Main service for ClickUp task and structure operations.
"""

import logging
from typing import List

from backend.src.domain.entities.clickup.folder_with_lists import FolderWithLists
from backend.src.domain.ports.input.i_clickup_task_service import IClickUpTaskService
from backend.src.domain.ports.output.clickup.i_clickup_reader import IClickUpReader


logger = logging.getLogger(__name__)


class ClickUpTaskService(IClickUpTaskService):
    """
    Application service for ClickUp operations: retrieving space structure
    and workspace members.

    Coordinates data fetching from ClickUp.

    Attributes:
        _clickup_reader (IClickUpReader): ClickUp reader port.
    """

    def __init__(self, clickup_reader: IClickUpReader):
        """
        Initialize the service with a ClickUp reader port.

        Args:
            clickup_reader (IClickUpReader): ClickUp reader port.
        """
        self._clickup_reader = clickup_reader

    def get_space_structure(self, space_id: str) -> List[FolderWithLists]:
        """
        Retrieve the structure of a ClickUp space.

        Args:
            space_id (str): ClickUp space identifier.

        Returns:
            List[FolderWithLists]: List of folders representing the space structure.
        """
        logger.info("Fetching space structure with lists. space_id=%s.", space_id)

        result = self._clickup_reader.get_space_full_structure(space_id)

        logger.info(
            "Space structure with lists fetched successfully. space_id=%s folders=%d.",
            space_id,
            len(result),
        )

        return result

    def get_workspace_members(self, space_id: str) -> List[dict]:
        """
        Retrieve all members of a ClickUp workspace.

        Args:
            space_id (str): ClickUp space identifier.

        Returns:
            List[dict]: List of workspace members.
        """
        logger.info("Fetching workspace members. space_id=%s.", space_id)

        result = self._clickup_reader.get_workspace_members(space_id)

        logger.info(
            "Workspace members fetched successfully. space_id=%s members=%d.",
            space_id,
            len(result),
        )

        return result