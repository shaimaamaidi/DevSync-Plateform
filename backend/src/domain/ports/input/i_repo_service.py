"""
Service port for Git repository management operations.

This module defines the IRepoService interface, which specifies operations
for managing Git repositories such as creation, update, retrieval, listing,
and deletion.

It acts as a contract for application-level services responsible for:
- Creating and updating repositories
- Retrieving repositories by different identifiers (id, name, url)
- Listing repositories with or without detailed information
- Deleting repositories
"""

from abc import ABC, abstractmethod
from typing import List

from backend.src.domain.entities.git_repo import (
    GitRepoCreateDTO,
    GitRepoDTO,
    GitRepoDetailDTO,
    GitRepoIdDTO,
    GitRepoNameDTO,
    GitRepoUpdateDTO,
)


class IRepoService(ABC):
    """
    Define repository service behavior required by the application.

    This interface represents the contract for managing Git repositories and
    their related metadata. It abstracts persistence and business logic for
    repository lifecycle operations.
    """

    @abstractmethod
    def add_repo(self, repo: GitRepoCreateDTO) -> GitRepoDTO:
        """
        Create a new repository.

        Args:
            repo (GitRepoCreateDTO): Repository create payload.

        Returns:
            GitRepoDTO: Created repository DTO.
        """
        pass

    @abstractmethod
    def update_repo(self, repo: GitRepoUpdateDTO) -> GitRepoDetailDTO:
        """
        Update an existing repository.

        Args:
            repo (GitRepoUpdateDTO): Repository update payload.

        Returns:
            GitRepoDetailDTO: Updated repository detail DTO.
        """
        pass

    @abstractmethod
    def get_by_id(self, repo: GitRepoIdDTO) -> GitRepoDetailDTO:
        """
        Fetch a repository by id.

        Args:
            repo (GitRepoIdDTO): Repository id wrapper.

        Returns:
            GitRepoDetailDTO: Repository detail DTO.
        """
        pass

    @abstractmethod
    def get_by_name(self, repo: GitRepoNameDTO) -> GitRepoDetailDTO:
        """
        Fetch a repository by name.

        Args:
            repo (GitRepoNameDTO): Repository name wrapper.

        Returns:
            GitRepoDetailDTO: Repository detail DTO.
        """
        pass

    @abstractmethod
    def get_by_url(self, url: str) -> GitRepoDTO:
        """
        Fetch a repository by URL.

        Args:
            url (str): Repository URL.

        Returns:
            GitRepoDTO: Repository DTO.
        """
        pass

    @abstractmethod
    def get_all(self) -> List[GitRepoDTO]:
        """
        Return all repositories.

        Returns:
            List[GitRepoDTO]: List of repository DTOs.
        """
        pass

    def get_all_with_details(self) -> List[GitRepoDetailDTO]:
        """
        Return all repositories with details.

        Returns:
            List[GitRepoDetailDTO]: List of repository detail DTOs.
        """
        pass

    @abstractmethod
    def delete(self, repo: GitRepoIdDTO) -> bool:
        """
        Delete a repository by id.

        Args:
            repo (GitRepoIdDTO): Repository id wrapper.

        Returns:
            bool: True when deletion succeeds.
        """
        pass
