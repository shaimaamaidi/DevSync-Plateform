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


logger = logging.getLogger(__name__)

router = APIRouter()


def get_clickup_structure_metadata_use_case(request: Request) -> ClickUpStructureMetadataUseCase:
    """
    Retrieve the ClickUp structure metadata use case instance.

    Singleton initialized at application startup. Provides read-only access
    to ClickUp workspace structural data (folders, lists).

    Args:
        request (Request): The incoming FastAPI request object.

    Returns:
        ClickUpStructureMetadataUseCase: The initialized metadata use case.

    Raises:
        ServiceUnavailableException:
            If the use case is not initialized in the application state.
    """
    try:
        use_case = request.app.state.workflow_container.clickup_structure_metadata_use_case

        if use_case is None:
            raise ServiceUnavailableException("ClickUp structure metadata use case is not initialized.")

        return use_case

    except ServiceUnavailableException:
        raise

    except Exception as e:
        logger.exception("Failed to retrieve ClickUp structure metadata use case: %s", str(e))
        raise ServiceUnavailableException("ClickUp structure metadata service is unavailable.") from e


@router.get(
    "/spaces/{space_id}/metadata",
    response_model=List[FolderWithListsMetadata],
    summary="Get ClickUp space structure metadata",
    description=(
        "Retrieve structural metadata for a ClickUp space, "
        "including its folders and associated lists."
    ),
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
    logger.info("GET /clickup/structure/spaces/%s/metadata", space_id)

    return use_case.get_space_structure_metadata(space_id)