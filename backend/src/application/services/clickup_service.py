"""
ClickUp service module.

This module provides the ClickUpService class, which handles use cases related to ClickUp spaces, such as creation, update, retrieval, and listing.
It coordinates persistence and business logic for ClickUp space management.

Classes:
    ClickUpService: Main service for ClickUp space operations.
"""

import logging
from typing import List

from backend.src.domain.entities.clickup_space import (
    ClickUpSpaceCreateDTO,
    ClickUpSpaceDTO,
    ClickUpSpaceDetailDTO,
    ClickUpSpaceLightDTO,
    ClickUpSpaceUpdateDTO,
)
from backend.src.domain.ports.repositories.i_clickup_repository import IClickUpRepository


logger = logging.getLogger(__name__)


class ClickUpService:
    """
    Application service for ClickUp space use cases: creation, update, retrieval, and listing.

    Coordinates persistence and business logic for ClickUp space management.

    Attributes:
        _repo (IClickUpRepository): ClickUp persistence port.
    """

    def __init__(self, clickup_repo: IClickUpRepository):
        """
        Initialize the service with a ClickUp repository port.

        Args:
            clickup_repo (IClickUpRepository): ClickUp persistence port.
        """
        self._repo = clickup_repo
        
    def add_space(self, space: ClickUpSpaceCreateDTO) -> ClickUpSpaceDTO:
        """
        Create a new ClickUp space.

        Args:
            space (ClickUpSpaceCreateDTO): ClickUp space create payload.

        Returns:
            ClickUpSpaceDTO: Created space DTO.
        """
        logger.info("Adding new ClickUp space: space_code=%s, name=%s.", space.space_code, space.name)
        
        result = self._repo.save(space)

        logger.info("ClickUp space added successfully: id=%s, space_code=%s.", result.id, result.space_code)

        return result

    def update_space(self, space: ClickUpSpaceUpdateDTO) -> ClickUpSpaceDetailDTO:
        """
        Update an existing ClickUp space.

        Args:
            space (ClickUpSpaceUpdateDTO): ClickUp space update payload.

        Returns:
            ClickUpSpaceDetailDTO: Updated space detail DTO.
        """
        logger.info("Updating ClickUp space: id=%s, space_code=%s.", space.id, space.space_code)
        
        result = self._repo.update(space)

        logger.info("ClickUp space updated successfully: id=%s, space_code=%s.", result.id, result.space_code)

        return result

    def get_by_id(self, space_id: int) -> ClickUpSpaceDetailDTO:
        """
        Fetch a ClickUp space by id.

        Args:
            space_id (int): ClickUp space identifier.

        Returns:
            ClickUpSpaceDetailDTO: ClickUp space detail DTO.
        """
        logger.info("Fetching ClickUp space by ID: id=%s.", space_id)
        
        result = self._repo.find_by_id(space_id)

        logger.info("ClickUp space fetched successfully: id=%s, space_code=%s.", result.id, result.space_code)

        return result

    def get_by_space_code(self, space_code: str) -> ClickUpSpaceDTO:
        """
        Fetch a ClickUp space by space code.

        Args:
            space_code (str): ClickUp space code.

        Returns:
            ClickUpSpaceDTO: ClickUp space DTO.
        """
        logger.info("Fetching ClickUp space by space_code: %s.", space_code)

        result = self._repo.find_by_space_code(space_code)

        logger.info("ClickUp space fetched successfully: id=%s, space_code=%s.", result.id, result.space_code)

        return result

    def get_all(self) -> List[ClickUpSpaceDTO]:
        """
        Return all ClickUp spaces.

        Returns:
            List[ClickUpSpaceDTO]: List of ClickUp space DTOs.
        """
        logger.info("Fetching all ClickUp spaces.")

        results = self._repo.find_all()

        logger.info("ClickUp spaces %s Fetched successfully.", len(results))

        return results

    def get_all_light(self) -> List[ClickUpSpaceLightDTO]:
        """
        Return all ClickUp spaces in light form.

        Returns:
            List[ClickUpSpaceLightDTO]: List of ClickUp space light DTOs.
        """
        logger.info("Fetching all ClickUp spaces (light).")

        results = self._repo.find_all_light()

        logger.info("ClickUp spaces (light) %s Fetched successfully.", len(results))

        return results

    def delete(self, space_id: int) -> bool:
        """
        Delete a ClickUp space by id.

        Args:
            space_id (int): ClickUp space identifier.

        Returns:
            bool: True when deletion succeeds.
        """
        logger.info("Deleting ClickUp space: id=%s.", space_id)
        
        result = self._repo.delete(space_id)

        logger.info("ClickUp space deleted successfully: id=%s.", space_id)

        return result