"""Application service for ClickUp spaces."""

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
    """Coordinate ClickUp space use cases."""
    def __init__(self, clickup_repo: IClickUpRepository):
        """Initialize the service with a ClickUp repository port.

        Args:
            clickup_repo: ClickUp persistence port.
        """
        self._repo = clickup_repo
        
    def add_space(self, space: ClickUpSpaceCreateDTO) -> ClickUpSpaceDTO:
        """Create a new ClickUp space.

        Args:
            space: ClickUp space create payload.

        Returns:
            Created space DTO.
        """
        logger.info("Adding new ClickUp space: space_code=%s, name=%s.", space.space_code, space.name)
        
        result = self._repo.save(space)

        logger.info("ClickUp space added successfully: id=%s, space_code=%s.", result.id, result.space_code)

        return result

    def update_space(self, space: ClickUpSpaceUpdateDTO) -> ClickUpSpaceDetailDTO:
        """Update an existing ClickUp space.

        Args:
            space: ClickUp space update payload.

        Returns:
            Updated space detail DTO.
        """
        logger.info("Updating ClickUp space: id=%s, space_code=%s.", space.id, space.space_code)
        
        result = self._repo.update(space)

        logger.info("ClickUp space updated successfully: id=%s, space_code=%s.", result.id, result.space_code)

        return result

    def get_by_id(self, space_id: int) -> ClickUpSpaceDetailDTO:
        """Fetch a ClickUp space by id.

        Args:
            space_id: ClickUp space identifier.

        Returns:
            ClickUp space detail DTO.
        """
        logger.info("Fetching ClickUp space by ID: id=%s.", space_id)
        
        result = self._repo.find_by_id(space_id)

        logger.info("ClickUp space fetched successfully: id=%s, space_code=%s.", result.id, result.space_code)

        return result

    def get_by_space_code(self, space_code: str) -> ClickUpSpaceDTO:
        """Fetch a ClickUp space by space code.

        Args:
            space_code: ClickUp space code.

        Returns:
            ClickUp space DTO.
        """
        logger.info("Fetching ClickUp space by space_code: %s.", space_code)

        result = self._repo.find_by_space_code(space_code)

        logger.info("ClickUp space fetched successfully: id=%s, space_code=%s.", result.id, result.space_code)

        return result

    def get_all(self) -> List[ClickUpSpaceDTO]:
        """Return all ClickUp spaces.

        Returns:
            List of ClickUp space DTOs.
        """
        logger.info("Fetching all ClickUp spaces.")

        results = self._repo.find_all()

        logger.info("Fetched %s ClickUp spaces successfully.", len(results))

        return results

    def get_all_light(self) -> List[ClickUpSpaceLightDTO]:
        """Return all ClickUp spaces in light form.

        Returns:
            List of ClickUp space light DTOs.
        """
        logger.info("Fetching all ClickUp spaces (light).")

        results = self._repo.find_all_light()

        logger.info("Fetched %s ClickUp spaces (light) successfully.", len(results))

        return results

    def delete(self, space_id: int) -> bool:
        """Delete a ClickUp space by id.

        Args:
            space_id: ClickUp space identifier.

        Returns:
            True when deletion succeeds.
        """
        logger.info("Deleting ClickUp space: id=%s.", space_id)
        
        result = self._repo.delete(space_id)

        logger.info("ClickUp space deleted successfully: id=%s.", space_id)

        return result