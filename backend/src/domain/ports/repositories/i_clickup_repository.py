"""
Repository port for ClickUp space persistence.

This module defines the IClickUpRepository interface, which specifies persistence operations
for ClickUp space entities, including creation, update, retrieval, listing, and deletion.
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

    This interface represents the contract for storing and retrieving ClickUp space data
    from a persistence layer such as a database.
    """

    @abstractmethod
    def save(self, space: ClickUpSpaceCreateDTO) -> ClickUpSpaceDTO:
        """
        Persist a new ClickUp space.

        Args:
            space (ClickUpSpaceCreateDTO): ClickUp space creation data.

        Returns:
            ClickUpSpaceDTO: Created ClickUp space DTO.
        """
        pass

    @abstractmethod
    def update(self, space: ClickUpSpaceUpdateDTO) -> ClickUpSpaceDetailDTO:
        """
        Update an existing ClickUp space.

        Args:
            space (ClickUpSpaceUpdateDTO): ClickUp space update data.

        Returns:
            ClickUpSpaceDetailDTO: Updated ClickUp space details.
        """
        pass

    @abstractmethod
    def find_by_id(self, space_id: int) -> ClickUpSpaceDetailDTO:
        """
        Retrieve a ClickUp space by its identifier.

        Args:
            space_id (int): ClickUp space identifier in BDD.

        Returns:
            ClickUpSpaceDetailDTO: ClickUp space details.
        """
        pass

    @abstractmethod
    def find_by_space_code(self, space_code: str) -> ClickUpSpaceDTO:
        """
        Retrieve a ClickUp space by its space code.

        Args:
            space_code (str): ClickUp space code.

        Returns:
            ClickUpSpaceDTO: ClickUp space data.
        """
        pass

    @abstractmethod
    def find_by_name(self, name: str) -> ClickUpSpaceDTO | None:
        """
        Fetch a ClickUp space by name, returns None if not found.
        Used for existence checks before creation.

        Args:
            name (str): ClickUp space name.

        Returns:
            ClickUpSpaceDTO | None: ClickUp space DTO or None if not found.
        """
        pass

    @abstractmethod
    def find_all(self) -> List[ClickUpSpaceDTO]:
        """
        Retrieve all ClickUp spaces.

        Returns:
            List[ClickUpSpaceDTO]: List of ClickUp spaces.
        """
        pass

    @abstractmethod
    def find_all_light(self) -> List[ClickUpSpaceLightDTO]:
        """
        Retrieve all ClickUp spaces in lightweight form.

        Returns:
            List[ClickUpSpaceLightDTO]: List of simplified ClickUp spaces.
        """
        pass

    @abstractmethod
    def delete(self, space_id: int) -> bool:
        """
        Delete a ClickUp space by its identifier.

        Args:
            space_id (int): ClickUp space identifier.

        Returns:
            bool: True if deletion succeeds, otherwise False.
        """
        pass