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
from backend.src.domain.entities.clickup_space import (
    ClickUpSpaceCreateDTO,
    ClickUpSpaceDTO,
    ClickUpSpaceDetailDTO,
    ClickUpSpaceLightDTO,
    ClickUpSpaceUpdateDTO,
)
from backend.src.infrastructure.di.container import Container
from backend.src.presentation.api.deps import get_container


logger = logging.getLogger(__name__)


router = APIRouter()


@router.get("/", response_model=list[ClickUpSpaceDTO])
def get_all_spaces(container: Container = Depends(get_container)) -> list[ClickUpSpaceDTO]:
    """
    Return all ClickUp spaces.

    Args:
        container (Container): Dependency injection container.

    Returns:
        list[ClickUpSpaceDTO]: List of all ClickUp spaces.
    """
    logger.info("Fetching all ClickUp spaces.")
    
    results = container.clickup_service.get_all()

    logger.info("Retrieved %d ClickUp spaces.", len(results))

    return results

@router.get("/light", response_model=list[ClickUpSpaceLightDTO])
def get_all_light(container: Container = Depends(get_container)) -> list[ClickUpSpaceLightDTO]:
    """
    Return all ClickUp spaces in light form.

    Args:
        container (Container): Dependency injection container.

    Returns:
        list[ClickUpSpaceLightDTO]: List of all ClickUp spaces (light version).
    """
    logger.info("Fetching all ClickUp spaces (light version).")

    results = container.clickup_service.get_all_light()

    logger.info("Retrieved %d ClickUp spaces (light).", len(results))

    return results

@router.get("/{space_id}", response_model=ClickUpSpaceDetailDTO)
def get_space_by_id(space_id: int, container: Container = Depends(get_container)) -> ClickUpSpaceDetailDTO:
    """
    Fetch a ClickUp space by id.

    Args:
        space_id (int): The ClickUp space ID.
        container (Container): Dependency injection container.

    Returns:
        ClickUpSpaceDetailDTO: The ClickUp space details.
    """
    logger.info("Fetching ClickUp space by id=%s.", space_id)

    result = container.clickup_service.get_by_id(space_id)

    logger.info("ClickUp space retrieved successfully: id=%s.", space_id)

    return result

@router.post("/", response_model=ClickUpSpaceDTO)
def create_space(space: ClickUpSpaceCreateDTO, container: Container = Depends(get_container)) -> ClickUpSpaceDTO:
    """
    Create a ClickUp space.

    Args:
        space (ClickUpSpaceCreateDTO): The ClickUp space creation payload.
        container (Container): Dependency injection container.

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

@router.put("/{space_id}", response_model=ClickUpSpaceDetailDTO)
def update_space(space_id: int, space: ClickUpSpaceUpdateDTO, container: Container = Depends(get_container)) -> ClickUpSpaceDetailDTO:
    """
    Update a ClickUp space by id.

    Args:
        space_id (int): The ClickUp space ID.
        space (ClickUpSpaceUpdateDTO): The update payload.
        container (Container): Dependency injection container.

    Returns:
        ClickUpSpaceDetailDTO: The updated ClickUp space details.
    """
    logger.info(
        "Updating ClickUp space: id=%s.",
    
        space_id,
    )

    space.id = space_id
    result = container.clickup_service.update_space(space)

    logger.info(
        "ClickUp space updated successfully: id=%s.",
        space_id,
    )

    return result

@router.delete("/{space_id}", response_model=bool)
def delete_space(space_id: int, container: Container = Depends(get_container)) -> bool:
    """
    Delete a ClickUp space by id.

    Args:
        space_id (int): The ClickUp space ID.
        container (Container): Dependency injection container.

    Returns:
        bool: True if deletion was successful.
    """
    logger.info("Deleting ClickUp space: id=%s.", space_id)

    result = container.clickup_service.delete(space_id)

    logger.info("ClickUp space deleted successfully: id=%s.", space_id)

    return result