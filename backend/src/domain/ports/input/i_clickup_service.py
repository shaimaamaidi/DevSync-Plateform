"""
Service port for ClickUp space management.

This module defines the IClickUpService interface, which specifies operations
for managing ClickUp spaces such as creation, update, retrieval, listing, and deletion.

It acts as a contract for application-level services responsible for:
- Creating and updating ClickUp spaces
- Retrieving spaces (by id or code)
- Listing spaces in full or lightweight form
- Deleting spaces
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


class IClickUpService(ABC):
    """
    Define ClickUp space service behavior required by the application.

    This interface represents the contract for managing ClickUp spaces,
    abstracting persistence and external ClickUp integration logic.
    """

    @abstractmethod
    def add_space(self, space: ClickUpSpaceCreateDTO) -> ClickUpSpaceDTO:
        """
        Create a new ClickUp space.

        Args:
            space (ClickUpSpaceCreateDTO): ClickUp space create payload.

        Returns:
            ClickUpSpaceDTO: Created space DTO.
        """
        pass

    @abstractmethod
    def update_space(self, space: ClickUpSpaceUpdateDTO) -> ClickUpSpaceDetailDTO:
        """
        Update an existing ClickUp space.

        Args:
            space (ClickUpSpaceUpdateDTO): ClickUp space update payload.

        Returns:
            ClickUpSpaceDetailDTO: Updated space detail DTO.
        """
        pass

    @abstractmethod
    def get_by_id(self, space_id: int) -> ClickUpSpaceDetailDTO:
        """
        Fetch a ClickUp space by id.

        Args:
            space_id (int): ClickUp space identifier.

        Returns:
            ClickUpSpaceDetailDTO: ClickUp space detail DTO.
        """
        pass

    @abstractmethod
    def get_by_space_code(self, space_code: str) -> ClickUpSpaceDTO:
        """
        Fetch a ClickUp space by space code.

        Args:
            space_code (str): ClickUp space code.

        Returns:
            ClickUpSpaceDTO: ClickUp space DTO.
        """
        pass

    @abstractmethod
    def get_all(self) -> List[ClickUpSpaceDTO]:
        """
        Return all ClickUp spaces.

        Returns:
            List[ClickUpSpaceDTO]: List of ClickUp space DTOs.
        """
        pass

    @abstractmethod
    def get_all_light(self) -> List[ClickUpSpaceLightDTO]:
        """
        Return all ClickUp spaces in light form.

        Returns:
            List[ClickUpSpaceLightDTO]: List of ClickUp space light DTOs.
        """
        pass

    @abstractmethod
    def delete(self, space_id: int) -> bool:
        """
        Delete a ClickUp space by id.

        Args:
            space_id (int): ClickUp space identifier.

        Returns:
            bool: True when deletion succeeds.
        """
        pass