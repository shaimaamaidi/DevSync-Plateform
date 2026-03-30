"""
Repository port for ClickUp space persistence.

This module defines the IClickUpRepository interface, which specifies persistence operations for ClickUp space entities.
"""

from abc import ABC, abstractmethod
from typing import List

from backend.src.domain.entities.clickup_space import (
    ClickUpSpaceCreateDTO,
    ClickUpSpaceDTO,
    ClickUpSpaceDetailDTO,
    ClickUpSpaceLightDTO,
    ClickUpSpaceUpdateDTO,
)


class IClickUpRepository(ABC):
    """
    Define persistence operations for ClickUp spaces.
    """
    @abstractmethod
    def save(self, space: ClickUpSpaceCreateDTO) -> ClickUpSpaceDTO:
        """Persist a new ClickUp space.

        Args:
            space: ClickUp space create DTO.

        Returns:
            Created ClickUp space DTO.
        """
        pass

    @abstractmethod
    def update(self, space: ClickUpSpaceUpdateDTO) -> ClickUpSpaceDetailDTO:
        """Persist updates for a ClickUp space.

        Args:
            space: ClickUp space update DTO.

        Returns:
            Updated ClickUp space detail DTO.
        """
        pass

    @abstractmethod
    def find_by_id(self, space_id: int) -> ClickUpSpaceDetailDTO:
        """Find a ClickUp space by id.

        Args:
            space_id: ClickUp space id.

        Returns:
            ClickUp space detail DTO.
        """
        pass

    @abstractmethod
    def find_by_space_code(self, space_code: str) -> ClickUpSpaceDTO:
        """Find a ClickUp space by space code.

        Args:
            space_code: ClickUp space code.

        Returns:
            ClickUp space DTO.
        """
        pass

    @abstractmethod
    def find_all(self) -> List[ClickUpSpaceDTO]:
        """Return all ClickUp spaces.

        Returns:
            List of ClickUp space DTOs.
        """
        pass

    @abstractmethod
    def find_all_light(self) -> List[ClickUpSpaceLightDTO]:
        """Return all ClickUp spaces in light form.

        Returns:
            List of ClickUp space light DTOs.
        """
        pass

    @abstractmethod
    def delete(self, space_id: int) -> bool:
        """Delete a ClickUp space by id.

        Args:
            space_id: ClickUp space id.

        Returns:
            True when deletion succeeds.
        """
        pass        
