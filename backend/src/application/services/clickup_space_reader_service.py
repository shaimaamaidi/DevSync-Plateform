"""
ClickUp task service module.

This module provides the ClickUpTaskService class, which manages ClickUp-related
operations such as retrieving space structure and workspace members.
It also handles caching for performance optimization.

Classes:
    ClickUpTaskService: Main service for ClickUp task and structure operations.
"""

import logging
from typing import List

from backend.src.domain.entities.clickup.folder import Folder
from backend.src.domain.ports.input.i_clickup_task_service import IClickUpTaskService
from backend.src.domain.ports.output.clickup.i_clickup_reader import IClickUpReader


logger = logging.getLogger(__name__)


class ClickUpTaskService(IClickUpTaskService):
    """
    Application service for ClickUp operations: retrieving space structure
    and workspace members.

    Coordinates data fetching from ClickUp and applies caching to optimize performance.

    Attributes:
        _clickup_reader (IClickUpReader): ClickUp reader port.
        _cache (dict[str, List[Folder]]): In-memory cache for space structures.
    """

    def __init__(self, clickup_reader: IClickUpReader):
        """
        Initialize the service with a ClickUp reader port.

        Args:
            clickup_reader (IClickUpReader): ClickUp reader port.
        """
        self._clickup_reader = clickup_reader
        self._cache: dict[str, List[Folder]] = {}

    def get_space_structure(self, space_id: str) -> List[Folder]:
        """
        Retrieve the structure of a ClickUp space.

        Uses an in-memory cache to avoid redundant API calls.

        Args:
            space_id (str): ClickUp space identifier.

        Returns:
            List[Folder]: List of folders representing the space structure.
        """
        logger.info("Fetching space structure. space_id=%s.", space_id)

        if space_id not in self._cache:
            self._cache[space_id] = self._clickup_reader.get_space_structure(space_id)

        result = self._cache[space_id]

        logger.info(
            "Space structure fetched successfully. space_id=%s folders=%d.",
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

    def invalidate(self, space_id: str) -> None:
        """
        Invalidate the cache for a given space.

        Typically called after a write operation to force a fresh fetch
        on the next retrieval.

        Args:
            space_id (str): ClickUp space identifier.
        """
        logger.info("Invalidating cache. space_id=%s.", space_id)
        self._cache.pop(space_id, None)
        logger.info("Cache invalidated successfully. space_id=%s.", space_id)