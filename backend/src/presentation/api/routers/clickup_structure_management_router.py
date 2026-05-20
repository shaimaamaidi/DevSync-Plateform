
"""
ClickUp structure creation API routes.

This module defines API endpoints for creating ClickUp workspace structure
elements such as spaces, folders, lists, and custom statuses.

It acts as the presentation layer for workspace provisioning operations,
delegating business logic to the ClickUpStructureManagementUseCase.

Routes:
    POST /spaces: Create a new ClickUp space.
    POST /folders: Create a folder inside a ClickUp space.
    POST /lists: Create a list inside a space or folder.
    POST /lists/{list_id}/statuses: Add a custom status to a list.
"""

import logging

from fastapi import APIRouter, Depends, status

from backend.src.application.use_cases.clickup_structure_management_use_case import ClickUpStructureManagementUseCase
from backend.src.domain.entities.clickup.add_status_request import AddStatusRequest
from backend.src.domain.entities.clickup.create_folder_request import CreateFolderRequest
from backend.src.domain.entities.clickup.create_list_request import CreateListRequest
from backend.src.domain.entities.clickup.create_space_request import CreateSpaceRequest
from backend.src.domain.entities.clickup.folder_with_list_metadata import FolderWithListsMetadata
from backend.src.domain.entities.clickup.list_metadata import ClickUpListMetadata
from backend.src.domain.entities.clickup.member_invitation import ClickUpMemberInvitation
from backend.src.domain.entities.clickup_space import ClickUpSpaceDTO, ClickUpSpaceRegisterDTO
from backend.src.presentation.api.deps import get_clickup_structure_creation_use_case


logger = logging.getLogger(__name__)


router = APIRouter()


@router.post(
    "/spaces/register",
    response_model=ClickUpSpaceDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Register a ClickUp space",
    description="Validate a ClickUp space existence and persist it in the application layer."
)
def register_space(
    body: ClickUpSpaceRegisterDTO,
    use_case: ClickUpStructureManagementUseCase = Depends(get_clickup_structure_creation_use_case),
) -> ClickUpSpaceDTO:
    """
    Register a ClickUp space.

    Args:
        body (ClickUpSpaceRegisterDTO): Space registration payload.
        use_case (ClickUpStructureManagementUseCase): Injected use case.

    Returns:
        ClickUpSpaceDTO: Persisted space DTO.
    """
    logger.info("Registering ClickUp space: space_code=%s.", body.space_code)

    result =  use_case.register_space(body)

    logger.info("ClickUp space registered successfully: space_code=%s.", body.space_code)

    return result

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
    use_case: ClickUpStructureManagementUseCase = Depends(get_clickup_structure_creation_use_case),
) -> ClickUpSpaceDTO:
    """
    Create a ClickUp space.

    Args:
        body (CreateSpaceRequest): Space creation payload.
        use_case (ClickUpStructureManagementUseCase): Injected use case.

    Returns:
        ClickUpSpaceDTO: Created space DTO.
    """
    logger.info("Creating ClickUp space: space_name=%s.", body.space_name)

    result = use_case.create_space(body)

    logger.info("ClickUp space created successfully: space_name=%s.", body.space_name)

    return result
@router.delete(
    "/spaces/{space_id}",
    response_model=bool,
    status_code=status.HTTP_200_OK,
    summary="Delete a ClickUp space",
    description="Delete a ClickUp space from both ClickUp and the application layer.",
)
def delete_space(
    space_id: int,
    use_case: ClickUpStructureManagementUseCase = Depends(get_clickup_structure_creation_use_case),
) -> bool:
    """
    Delete a ClickUp space.

    Args:
        space_id (str): ClickUp space identifier (path param).
        use_case (ClickUpStructureManagementUseCase): Injected use case.

    Returns:
        bool: True if deletion succeeds.
    """
    logger.info("Deleting ClickUp space: space_id=%s.", space_id)

    result = use_case.delete_space(space_id)

    logger.info(
        "Deleted ClickUp space successfully: space_id=%s.",
        space_id,
    )

    return result

@router.post(
    "/members/invite",
    response_model=bool,
    status_code=status.HTTP_201_CREATED,
    summary="Invite a member to the ClickUp workspace",
    description="Send an invitation to a member to join the ClickUp workspace.",
)
def invite_member(
    body: ClickUpMemberInvitation,
    use_case: ClickUpStructureManagementUseCase = Depends(get_clickup_structure_creation_use_case),
) -> bool:
    """
    Invite a member to a ClickUp workspace.

    Args:
        body (ClickUpMemberInvitation): Member invitation payload.
        use_case (ClickUpStructureManagementUseCase): Injected use case.

    Returns:
        bool: True if the invitation succeeds.
    """
    logger.info(
        "Inviting member to ClickUp workspace: email=%s, role=%s.",
        body.email,
        body.role,
    )

    result = use_case.invite_member(body)

    logger.info(
        "Member invitation sent successfully: email=%s.",
        body.email,
    )

    return result

@router.delete(
    "/members/{member_id}",
    response_model=bool,
    status_code=status.HTTP_200_OK,
    summary="Remove a member from the ClickUp workspace",
    description="Remove a member from the ClickUp workspace by their database ID.",
)
def remove_member_from_workspace(
    member_id: int,
    use_case: ClickUpStructureManagementUseCase = Depends(get_clickup_structure_creation_use_case),
) -> bool:
    """
    Remove a member from the ClickUp workspace.

    Args:
        member_id (int): Member identifier in the database (path param).
        use_case (ClickUpStructureManagementUseCase): Injected use case.

    Returns:
        bool: True if removal succeeds.
    """
    logger.info("Removing member from ClickUp workspace: member_id=%s.", member_id)

    result = use_case.remove_member_from_workspace(member_id)

    logger.info("Member removed successfully from ClickUp workspace: member_id=%s.", member_id)

    return result

@router.post(
    "/folders",
    response_model=FolderWithListsMetadata,
    status_code=status.HTTP_201_CREATED,
    summary="Create a ClickUp folder",
    description="Create a new folder inside a ClickUp space.",
)
def create_folder(
    body: CreateFolderRequest,
    use_case: ClickUpStructureManagementUseCase = Depends(get_clickup_structure_creation_use_case),
) -> FolderWithListsMetadata:
    """
    Create a folder inside a ClickUp space.

    Args:
        body (CreateFolderRequest): Folder creation payload.
        use_case (ClickUpStructureManagementUseCase): Injected use case.

    Returns:
        FolderWithListsMetadata: Created folder metadata.
    """
    logger.info(
        "Creating ClickUp folder: space_id=%s, folder_name=%s.",
        body.space_id,
        body.name,
    )

    result = use_case.create_folder(body)

    logger.info(
        "Created ClickUp folder successfully: space_id=%s, folder_name=%s.",
        body.space_id,
        body.name,
    )

    return result


@router.post(
    "/lists",
    response_model=ClickUpListMetadata,
    status_code=status.HTTP_201_CREATED,
    summary="Create a ClickUp list",
    description="Create a new list inside a ClickUp space or folder.",
)
def create_list(
    body: CreateListRequest,
    use_case: ClickUpStructureManagementUseCase = Depends(get_clickup_structure_creation_use_case),
) -> ClickUpListMetadata:
    """
    Create a list inside a ClickUp space or folder.

    Args:
        body (CreateListRequest): List creation payload.
        use_case (ClickUpStructureManagementUseCase): Injected use case.

    Returns:
        ClickUpListMetadata: Created list metadata.
    """
    logger.info(
        "Creating ClickUp list: space_id=%s, folder_id=%s, list_name=%s.",
        body.space_id,
        body.folder_id,
        body.name,
    )

    result = use_case.create_list(body)

    logger.info(
        "Created ClickUp list successfully: list_name=%s.",
        body.name,
    )

    return result


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
    use_case: ClickUpStructureManagementUseCase = Depends(get_clickup_structure_creation_use_case),
) -> ClickUpListMetadata:
    """
    Add a status to a ClickUp list.

    Args:
        list_id (str): Target ClickUp list identifier (path param).
        body (AddStatusRequest): Status creation payload.
        use_case (ClickUpStructureManagementUseCase): Injected use case.

    Returns:
        ClickUpListMetadata: Updated list metadata.
    """
    logger.info(
        "Adding status to ClickUp list: list_id=%s, status=%s.",
        list_id,
        body.status,
    )

    body_with_list_id: AddStatusRequest = body.model_copy(update={"list_id": list_id})
    result = use_case.add_status(body_with_list_id)

    logger.info(
        "Status added successfully to ClickUp list: list_id=%s, status=%s.",
        list_id,
        body.status,
    )

    return result