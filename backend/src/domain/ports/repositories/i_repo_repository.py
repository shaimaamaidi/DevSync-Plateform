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
        """
        Persist a new repository.

        Args:
            repo (GitRepoCreateDTO): Create DTO.

        Returns:
            GitRepoDTO: Created repository DTO.
        """
        pass

    @abstractmethod
    def update(self, repo: GitRepoUpdateDTO) -> GitRepoDetailDTO:
        """
        Persist updates for a repository.

        Args:
            repo (GitRepoUpdateDTO): Update DTO.

        Returns:
            GitRepoDetailDTO: Updated repository detail.
        """
        pass

    @abstractmethod
    def find_by_id(self, repo_id: int) -> GitRepoDetailDTO:
        """
        Find a repository by id.

        Args:
            repo_id (int): Repository id.

        Returns:
            GitRepoDetailDTO: Repository detail DTO.
        """
        pass
        
    @abstractmethod
    def find_by_url(self, url: str) -> GitRepoDTO:
        """
        Find a repository by URL.

        Args:
            url (str): Repository URL.

        Returns:
            GitRepoDTO: Repository DTO.
        """
        pass

    @abstractmethod
    def find_by_name(self, name: str) -> GitRepoDetailDTO:
        """
        Find a repository by name.

        Args:
            name (str): Repository name.

        Returns:
            GitRepoDetailDTO: Repository detail DTO.
        """
        pass

    @abstractmethod
    def find_all(self) -> List[GitRepoDTO]:
        """
        Return all repositories.

        Returns:
            List[GitRepoDTO]: List of repository DTOs.
        """
        pass

    @abstractmethod
    def find_all_with_details(self) -> List[GitRepoDetailDTO]:
        """
        Return all repositories with details.

        Returns:
            List[GitRepoDetailDTO]: List of repository detail DTOs.
        """
        pass

    @abstractmethod
    def delete(self, repo_id: int) -> bool:
        """
        Delete a repository by id.

        Args:
            repo_id (int): Repository id.

        Returns:
            bool: True when deletion succeeds.
        """
        pass