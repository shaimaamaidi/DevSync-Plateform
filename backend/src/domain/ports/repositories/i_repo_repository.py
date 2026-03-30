"""
Repository port for Git repository persistence.

This module defines the IRepoRepository interface, which specifies persistence operations for Git repository entities.
"""

from abc import ABC, abstractmethod
from typing import List

from backend.src.domain.entities.git_repo import GitRepoCreateDTO, GitRepoDTO, GitRepoDetailDTO, GitRepoUpdateDTO


class IRepoRepository(ABC):
    """
    Define repository persistence operations for Git repositories.
    """
    @abstractmethod
    def save(self, repo: GitRepoCreateDTO) -> GitRepoDTO:
        """Persist a new repository.

        Args:
            repo: Create DTO.

        Returns:
            Created repository DTO.
        """
        pass

    @abstractmethod
    def update(self, repo: GitRepoUpdateDTO) -> GitRepoDetailDTO:
        """Persist updates for a repository.

        Args:
            repo: Update DTO.

        Returns:
            Updated repository detail.
        """
        pass

    @abstractmethod
    def find_by_id(self, repo_id: int) -> GitRepoDetailDTO:
        """Find a repository by id.

        Args:
            repo_id: Repository id.

        Returns:
            Repository detail DTO.
        """
        pass
        
    @abstractmethod
    def find_by_url(self, url: str) -> GitRepoDTO:
        """Find a repository by URL.

        Args:
            url: Repository URL.

        Returns:
            Repository DTO.
        """
        pass

    @abstractmethod
    def find_by_name(self, name: str) -> GitRepoDetailDTO:
        """Find a repository by name.

        Args:
            name: Repository name.

        Returns:
            Repository detail DTO.
        """
        pass

    @abstractmethod
    def find_all(self) -> List[GitRepoDTO]:
        """Return all repositories.

        Returns:
            List of repository DTOs.
        """
        pass

    @abstractmethod
    def find_all_with_details(self) -> List[GitRepoDetailDTO]:
        """Return all repositories with details.

        Returns:
            List of repository detail DTOs.
        """
        pass

    @abstractmethod
    def delete(self, repo_id: int) -> bool:
        """Delete a repository by id.

        Args:
            repo_id: Repository id.

        Returns:
            True when deletion succeeds.
        """
        pass