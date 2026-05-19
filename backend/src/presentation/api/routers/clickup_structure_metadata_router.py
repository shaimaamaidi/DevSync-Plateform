"""
ClickUp structure metadata API routes.

This module exposes endpoints for retrieving ClickUp workspace structure
metadata, including folders and lists associated with a given space.

It provides read-only access to ClickUp structural information through
the ClickUpStructureMetadataUseCase.

Routes:
    GET /spaces/{space_id}/metadata: Retrieve folders and lists metadata
    for a given ClickUp space.
"""

import logging
from typing import List

from fastapi import APIRouter, Depends, Request

from backend.src.application.use_cases.clickup_structure_metadata_use_case import ClickUpStructureMetadataUseCase
from backend.src.domain.entities.clickup.folder_with_list_metadata import FolderWithListsMetadata
from backend.src.domain.exceptions.system.service_unavailable_exception import ServiceUnavailableException
from backend.src.presentation.api.deps import get_clickup_structure_metadata_use_case

logger = logging.getLogger(__name__)


router = APIRouter()


@router.get(
    "/spaces/{space_id}/metadata",
    response_model=List[FolderWithListsMetadata],
    summary="Get ClickUp space structure metadata",
    description="Retrieve structural metadata for a ClickUp space, including its folders and associated lists."
)
def get_space_structure_metadata(
    space_id: str,
    use_case: ClickUpStructureMetadataUseCase = Depends(get_clickup_structure_metadata_use_case),
) -> List[FolderWithListsMetadata]:
    """
    Retrieve metadata of a ClickUp space structure.

    Args:
        space_id (str): ClickUp space identifier.
        use_case (ClickUpStructureMetadataUseCase): Injected use case.

    Returns:
        List[FolderWithListsMetadata]: Folders with their associated lists.
    """
    logger.info("Fetching ClickUp space structure metadata: space_id=%s.", space_id)

    results = use_case.get_space_structure_metadata(space_id)

    logger.info(
        "Fetched ClickUp space structure metadata successfully: space_id=%s, folders_count=%s.",
        space_id,
        len(results),
    )

    return results