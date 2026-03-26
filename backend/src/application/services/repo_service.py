"""Application service for Git repository operations."""

import logging
from typing import List

from backend.src.domain.entities.git_repo import (
    GitRepoCreateDTO,
    GitRepoDTO,
    GitRepoDetailDTO,
    GitRepoIdDTO,
    GitRepoNameDTO,
    GitRepoUpdateDTO,
)
from backend.src.domain.ports.repositories.i_repo_repository import IRepoRepository


logger = logging.getLogger(__name__)


class RepoService:
    """Coordinate Git repository use cases."""
    def __init__(self, repo_repo: IRepoRepository):
        """Initialize the service with a repository port.

        Args:
            repo_repo: Repository persistence port.
        """
        self._repo = repo_repo

    def add_repo(self, repo: GitRepoCreateDTO) -> GitRepoDTO:
        """Create a new repository.

        Args:
            repo: Repository create payload.

        Returns:
            Created repository DTO.
        """
        logger.info("Adding new repository: name=%s, url=%s.", repo.name, repo.url)

        result = self._repo.save(repo)

        logger.info("Repository added successfully: id=%s, name=%s.", result.id, result.name)

        return result

    def update_repo(self, repo: GitRepoUpdateDTO) -> GitRepoDetailDTO:
        """Update an existing repository.

        Args:
            repo: Repository update payload.

        Returns:
            Updated repository detail DTO.
        """
        logger.info("Updating repository: id=%s, name=%s.", repo.id, repo.name)

        result = self._repo.update(repo)

        logger.info("Repository updated successfully: id=%s, name=%s.", result.id, result.name)

        return result

    def get_by_id(self, repo: GitRepoIdDTO) -> GitRepoDetailDTO:
        """Fetch a repository by id.

        Args:
            repo: Repository id wrapper.

        Returns:
            Repository detail DTO.
        """
        logger.info("Fetching repository by id: %s.", repo.id)

        result = self._repo.find_by_id(repo.id)

        logger.info("Repository fetched successfully: id=%s, name=%s.", result.id, result.name)

        return result

    def get_by_name(self, repo: GitRepoNameDTO) -> GitRepoDetailDTO:
        """Fetch a repository by name.

        Args:
            repo: Repository name wrapper.

        Returns:
            Repository detail DTO.
        """
        logger.info("Fetching repository by name: %s.", repo.name)

        result = self._repo.find_by_name(repo.name)

        logger.info("Repository fetched successfully: id=%s, name=%s.", result.id, result.name)

        return result

    def get_by_url(self, url: str) -> GitRepoDTO:
        """Fetch a repository by URL.

        Args:
            url: Repository URL.

        Returns:
            Repository DTO.
        """
        logger.info("Fetching repository by URL: %s.", url)

        result = self._repo.find_by_url(url)

        logger.info("Repository fetched successfully: id=%s, url=%s.", result.id, result.url)

        return result

    def get_all(self) -> List[GitRepoDTO]:
        """Return all repositories.

        Returns:
            List of repository DTOs.
        """
        logger.info("Fetching all repositories.")

        results = self._repo.find_all()

        logger.info("Fetched %s repositories successfully.", len(results))

        return results

    def get_all_with_details(self) -> List[GitRepoDetailDTO]:
        """Return all repositories with details.

        Returns:
            List of repository detail DTOs.
        """
        logger.info("Fetching all repositories with details.")

        results = self._repo.find_all_with_details()

        logger.info("Fetched %s detailed repositories successfully.", len(results))

        return results

    def delete(self, repo: GitRepoIdDTO) -> bool:
        """Delete a repository by id.

        Args:
            repo: Repository id wrapper.

        Returns:
            True when deletion succeeds.
        """
        logger.info("Deleting repository: id=%s.", repo.id)

        result = self._repo.delete(repo.id)

        logger.info("Repository deleted successfully: id=%s.", repo.id)
        
        return result
