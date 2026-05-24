"""
ClickUp space API routes.

This module defines API endpoints for managing ClickUp spaces, including creation, retrieval, update, and deletion.

Routes:
    GET /: Return all ClickUp spaces.
    GET /light: Return all ClickUp spaces in light form.
    GET /{space_id}: Fetch a ClickUp space by id.
    POST /: Create a ClickUp space.
    PUT /{space_id}: Update a ClickUp space by id.
    DELETE /{space_id}: Delete a ClickUp space by id.
"""

import logging

from fastapi import APIRouter, Depends
from starlette import status

from backend.src.domain.entities.clickup_space import (
    ClickUpSpaceCreateDTO,
    ClickUpSpaceDTO,
    ClickUpSpaceDetailDTO,
    ClickUpSpaceLightDTO,
    ClickUpSpaceUpdateDTO,
)
from backend.src.infrastructure.di.persistence_container import PersistenceContainer
from backend.src.presentation.api.deps import get_persistence_container


logger = logging.getLogger(__name__)


router = APIRouter()


@router.get(
    "/",
    response_model=list[ClickUpSpaceDTO],
    status_code=status.HTTP_200_OK,
    summary="Get all ClickUp spaces",
    description=(
        "Retrieves the full list of ClickUp spaces stored in the system."
    )
)
def get_all_spaces(container: PersistenceContainer = Depends(get_persistence_container)) -> list[ClickUpSpaceDTO]:
    """
    Return all ClickUp spaces.

    Args:
        container (PersistenceContainer): Dependency injection container.

    Returns:
        list[ClickUpSpaceDTO]: List of all ClickUp spaces.
    """
    logger.info("Fetching all ClickUp spaces.")
    
    results = container.clickup_service.get_all()

    logger.info("Retrieved %d ClickUp spaces.", len(results))

    return results

@router.get(
    "/light",
    response_model=list[ClickUpSpaceLightDTO],
    status_code=status.HTTP_200_OK,
    summary="Get all ClickUp spaces (light version)",
    description=(
        "Retrieves a simplified version of ClickUp spaces with reduced fields "
        "for lightweight usage (e.g., dropdowns or listings)."
    )
)
def get_all_light(container: PersistenceContainer = Depends(get_persistence_container)) -> list[ClickUpSpaceLightDTO]:
    """
    Return all ClickUp spaces in light form.

    Args:
        container (PersistenceContainer): Dependency injection container.

    Returns:
        list[ClickUpSpaceLightDTO]: List of all ClickUp spaces (light version).
    """
    logger.info("Fetching all ClickUp spaces (light version).")

    results = container.clickup_service.get_all_light()

    logger.info("Retrieved %d ClickUp spaces (light).", len(results))

    return results

@router.get(
    "/{space_id}",
    response_model=ClickUpSpaceDetailDTO,
    status_code=status.HTTP_200_OK,
    summary="Get ClickUp space by ID",
    description=(
        "Fetches detailed information about a specific ClickUp space using its unique identifier."
    )
)
def get_space_by_id(space_id: int, container: PersistenceContainer = Depends(get_persistence_container)) -> ClickUpSpaceDetailDTO:
    """
    Fetch a ClickUp space by id.

    Args:
        space_id (int): The ClickUp space ID.
        container (PersistenceContainer): Dependency injection container.

    Returns:
        ClickUpSpaceDetailDTO: The ClickUp space details.
    """
    logger.info("Fetching ClickUp space by id=%s.", space_id)

    result = container.clickup_service.get_by_id(space_id)

    logger.info("ClickUp space retrieved successfully: id=%s.", space_id)

    return result

@router.post(
    "/",
    response_model=ClickUpSpaceDTO,
    status_code=status.HTTP_200_OK,
    summary="Get ClickUp space by ID",
    description=(
        "Fetches detailed information about a specific ClickUp space using its unique identifier."
    )
)
def create_space(space: ClickUpSpaceCreateDTO, container: PersistenceContainer = Depends(get_persistence_container)) -> ClickUpSpaceDTO:
    """
    Create a ClickUp space.

    Args:
        space (ClickUpSpaceCreateDTO): The ClickUp space creation payload.
        container (PersistenceContainer): Dependency injection container.

    Returns:
        ClickUpSpaceDTO: The created ClickUp space.
    """
    logger.info(
        "Creating ClickUp space: space_code=%s, name=%s.",
        space.space_code,
        space.name,
    )

    result = container.clickup_service.add_space(space)

    logger.info(
        "ClickUp space created successfully: space_code=%s.",
        result.space_code,
    )

    return result

@router.put(
    "/{space_id}",
    response_model=ClickUpSpaceDetailDTO,
    status_code=status.HTTP_200_OK,
    summary="Update a ClickUp space",
    description=(
        "Updates an existing ClickUp space identified by its ID with new provided values."
    )
)
def update_space(space_id: int, space: ClickUpSpaceUpdateDTO, container: PersistenceContainer = Depends(get_persistence_container)) -> ClickUpSpaceDetailDTO:
    """
    Update a ClickUp space by id.

    Args:
        space_id (int): The ClickUp space ID.
        space (ClickUpSpaceUpdateDTO): The update payload.
        container (PersistenceContainer): Dependency injection container.

    Returns:
        ClickUpSpaceDetailDTO: The updated ClickUp space details.
    """
    logger.info("Updating ClickUp space: id=%s.", space_id)

    space_with_id: ClickUpSpaceUpdateDTO = space.model_copy(update={"id": space_id})
    result = container.clickup_service.update_space(space_with_id)

    logger.info("ClickUp space updated successfully: id=%s.", space_id)

    return result

@router.delete(
    "/{space_id}",
    response_model=bool,
    status_code=status.HTTP_200_OK,
    summary="Update a ClickUp space",
    description=(
        "Updates an existing ClickUp space identified by its ID with new provided values."
    )
)
def delete_space(space_id: int, container: PersistenceContainer = Depends(get_persistence_container)) -> bool:
    """
    Delete a ClickUp space by id.

    Args:
        space_id (int): The ClickUp space ID.
        container (PersistenceContainer): Dependency injection container.

    Returns:
        bool: True if deletion was successful.
    """
    logger.info("Deleting ClickUp space: id=%s.", space_id)

    result = container.clickup_service.delete(space_id)

    logger.info("ClickUp space deleted successfully: id=%s.", space_id)

    return result