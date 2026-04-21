"""
Repository port for Git repository persistence.

This module defines the IRepoRepository interface, which specifies persistence operations
for Git repository entities, including creation, update, retrieval, listing, and deletion.
"""

from abc import ABC, abstractmethod
from typing import List

from backend.src.domain.entities.git_repo import (
    GitRepoCreateDTO,
    GitRepoDTO,
    GitRepoDetailDTO,
    GitRepoUpdateDTO,
)


class IRepoRepository(ABC):
    """
    Define repository persistence operations for Git repositories.

    This interface represents the contract for storing and managing Git repository data
    in a persistence layer such as a database, including access to both lightweight and
    detailed representations.
    """

    @abstractmethod
    def save(self, repo: GitRepoCreateDTO) -> GitRepoDTO:
        """
        Persist a new Git repository.

        Args:
            repo (GitRepoCreateDTO): Repository creation data.

        Returns:
            GitRepoDTO: Created repository.
        """
        pass

    @abstractmethod
    def update(self, repo: GitRepoUpdateDTO) -> GitRepoDetailDTO:
        """
        Update an existing Git repository.

        Args:
            repo (GitRepoUpdateDTO): Repository update data.

        Returns:
            GitRepoDetailDTO: Updated repository with full details.
        """
        pass

    @abstractmethod
    def find_by_id(self, repo_id: int) -> GitRepoDetailDTO:
        """
        Retrieve a repository by its identifier.

        Args:
            repo_id (int): Repository identifier.

        Returns:
            GitRepoDetailDTO: Repository details.
        """
        pass

    @abstractmethod
    def find_by_url(self, url: str) -> GitRepoDTO:
        """
        Retrieve a repository by its URL.

        Args:
            url (str): Repository URL.

        Returns:
            GitRepoDTO: Repository data.
        """
        pass

    @abstractmethod
    def find_by_name(self, name: str) -> GitRepoDetailDTO:
        """
        Retrieve a repository by its name.

        Args:
            name (str): Repository name.

        Returns:
            GitRepoDetailDTO: Repository details.
        """
        pass

    @abstractmethod
    def find_all(self) -> List[GitRepoDTO]:
        """
        Retrieve all repositories.

        Returns:
            List[GitRepoDTO]: List of repositories.
        """
        pass

    @abstractmethod
    def find_all_with_details(self) -> List[GitRepoDetailDTO]:
        """
        Retrieve all repositories with full details.

        Returns:
            List[GitRepoDetailDTO]: List of detailed repositories.
        """
        pass

    @abstractmethod
    def delete(self, repo_id: int) -> bool:
        """
        Delete a repository by its identifier.

        Args:
            repo_id (int): Repository identifier.

        Returns:
            bool: True if deletion succeeds, otherwise False.
        """
        pass