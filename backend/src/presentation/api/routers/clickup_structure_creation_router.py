
"""
ClickUp structure creation API routes.

This module defines API endpoints for creating ClickUp workspace structure
elements such as spaces, folders, lists, and custom statuses.

It acts as the presentation layer for workspace provisioning operations,
delegating business logic to the ClickUpStructureCreationUseCase.

Routes:
    POST /spaces: Create a new ClickUp space.
    POST /folders: Create a folder inside a ClickUp space.
    POST /lists: Create a list inside a space or folder.
    POST /lists/{list_id}/statuses: Add a custom status to a list.
"""

import logging

from fastapi import APIRouter, Depends, status

from backend.src.application.use_cases.clickup_structure_creation_use_case import ClickUpStructureCreationUseCase
from backend.src.domain.entities.clickup.add_status_request import AddStatusRequest
from backend.src.domain.entities.clickup.create_folder_request import CreateFolderRequest
from backend.src.domain.entities.clickup.create_list_request import CreateListRequest
from backend.src.domain.entities.clickup.create_space_request import CreateSpaceRequest
from backend.src.domain.entities.clickup.folder_with_list_metadata import FolderWithListsMetadata
from backend.src.domain.entities.clickup.list_metadata import ClickUpListMetadata
from backend.src.domain.entities.clickup_space import ClickUpSpaceDTO, ClickUpSpaceRegisterDTO
from backend.src.presentation.api.deps import get_clickup_structure_creation_use_case


logger = logging.getLogger(__name__)


router = APIRouter()


@router.post(
    "/spaces/register",
    response_model=ClickUpSpaceDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Register a ClickUp space",
    description=(
        "Validate a ClickUp space existence and persist it "
        "in the application layer."
    ),
)
def register_space(
    body: ClickUpSpaceRegisterDTO,
    use_case: ClickUpStructureCreationUseCase = Depends(get_clickup_structure_creation_use_case),
) -> ClickUpSpaceDTO:
    """
    Register a ClickUp space.

    Args:
        body (ClickUpSpaceRegisterDTO): Space registration payload.
        use_case (ClickUpStructureCreationUseCase): Injected use case.

    Returns:
        ClickUpSpaceDTO: Persisted space DTO.
    """
    logger.info("POST /clickup/structure/spaces/register. space_code=%s.", body.space_code)

    return use_case.register_space(body)

@router.post(
    "/spaces",
    response_model=ClickUpSpaceDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create a ClickUp space",
    description=(
        "Create a new ClickUp space and persist it "
        "in the application layer."
    ),
)
def create_space(
    body: CreateSpaceRequest,
    use_case: ClickUpStructureCreationUseCase = Depends(get_clickup_structure_creation_use_case),
) -> ClickUpSpaceDTO:
    """
    Create a ClickUp space.

    Args:
        body (CreateSpaceRequest): Space creation payload.
        use_case (ClickUpStructureCreationUseCase): Injected use case.

    Returns:
        ClickUpSpaceDTO: Created space DTO.
    """
    logger.info("POST /clickup/structure/spaces. space_id=%s.", body.space_id)

    return use_case.create_space(body)


@router.post(
    "/folders",
    response_model=FolderWithListsMetadata,
    status_code=status.HTTP_201_CREATED,
    summary="Create a ClickUp folder",
    description="Create a new folder inside a ClickUp space.",
)
def create_folder(
    body: CreateFolderRequest,
    use_case: ClickUpStructureCreationUseCase = Depends(get_clickup_structure_creation_use_case),
) -> FolderWithListsMetadata:
    """
    Create a folder inside a ClickUp space.

    Args:
        body (CreateFolderRequest): Folder creation payload.
        use_case (ClickUpStructureCreationUseCase): Injected use case.

    Returns:
        FolderWithListsMetadata: Created folder metadata.
    """
    logger.info(
        "POST /clickup/structure/folders. space_id=%s folder_name=%s.",
        body.space_id,
        body.name,
    )

    return use_case.create_folder(body)


@router.post(
    "/lists",
    response_model=ClickUpListMetadata,
    status_code=status.HTTP_201_CREATED,
    summary="Create a ClickUp list",
    description="Create a new list inside a ClickUp space or folder.",
)
def create_list(
    body: CreateListRequest,
    use_case: ClickUpStructureCreationUseCase = Depends(get_clickup_structure_creation_use_case),
) -> ClickUpListMetadata:
    """
    Create a list inside a ClickUp space or folder.

    Args:
        body (CreateListRequest): List creation payload.
        use_case (ClickUpStructureCreationUseCase): Injected use case.

    Returns:
        ClickUpListMetadata: Created list metadata.
    """
    logger.info(
        "POST /clickup/structure/lists. space_id=%s folder_id=%s list_name=%s.",
        body.space_id,
        body.folder_id,
        body.name,
    )

    return use_case.create_list(body)


@router.post(
    "/lists/{list_id}/statuses",
    response_model=ClickUpListMetadata,
    status_code=status.HTTP_201_CREATED,
    summary="Add a status to a ClickUp list",
    description="Add a custom status to an existing ClickUp list.",
)
def add_status(
    list_id: str,
    body: AddStatusRequest,
    use_case: ClickUpStructureCreationUseCase = Depends(get_clickup_structure_creation_use_case),
) -> ClickUpListMetadata:
    """
    Add a status to a ClickUp list.

    Args:
        list_id (str): Target ClickUp list identifier (path param).
        body (AddStatusRequest): Status creation payload.
        use_case (ClickUpStructureCreationUseCase): Injected use case.

    Returns:
        ClickUpListMetadata: Updated list metadata.
    """
    logger.info(
        "POST /clickup/structure/lists/%s/statuses. status=%s.",
        list_id,
        body.status,
    )

    # list_id vient du path — on s'assure de la cohérence avec le body
    body.list_id = list_id

    return use_case.add_status(body)