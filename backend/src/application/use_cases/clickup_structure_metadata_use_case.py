"""
ClickUp space structure metadata use case module.

This module provides the ClickUpStructureMetadataUseCase class, which is responsible
for retrieving metadata about a ClickUp space structure (folders, lists, and related
structural information).

It acts as an application-level use case that delegates data retrieval to the
ClickUpReader port without applying business mutations or caching.

Classes:
    ClickUpStructureMetadataUseCase: Use case for retrieving ClickUp space structure metadata.
"""

import logging
from typing import List

from backend.src.domain.entities.clickup.folder_with_list_metadata import FolderWithListsMetadata
from backend.src.domain.ports.input.i_clickup_structure_metadata_use_case import IClickUpStructureMetadataUseCase
from backend.src.domain.ports.output.clickup.i_clickup_reader import IClickUpReader


logger = logging.getLogger(__name__)


class ClickUpStructureMetadataUseCase(IClickUpStructureMetadataUseCase):
    """
    Application use case for retrieving ClickUp space structure metadata.

    This class provides read-only access to ClickUp structural metadata such as
    folders and lists inside a space. It delegates retrieval to the ClickUpReader
    port and does not apply caching or modification logic.

    Attributes:
        _clickup_reader (IClickUpReader): Port used to fetch data from ClickUp API.
    """

    def __init__(self, clickup_reader: IClickUpReader):
        """
        Initialize the use case with a ClickUp reader port.

        Args:
            clickup_reader (IClickUpReader): ClickUp reader port implementation.
        """
        self._clickup_reader = clickup_reader

    def get_space_structure_metadata(self, space_id: str) -> List[FolderWithListsMetadata]:
        """
        Retrieve metadata of a ClickUp space structure.

        This includes structural information such as folders and lists
        within the specified space.

        Args:
            space_id (str): ClickUp space identifier.

        Returns:
            List[FolderWithListsMetadata]: List of folders with their associated metadata.
        """
        logger.info("Fetching space metadata. space_id=%s.", space_id)

        results = self._clickup_reader.get_space_structure_metadata(space_id)

        logger.info(
            "Space metadata fetched successfully. space_id=%s folders=%d.",
            space_id,
            len(results),
        )

        return results