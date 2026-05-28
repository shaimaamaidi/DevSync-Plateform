"""
Use case port for GitHub repository creation.

This module defines the ICreateGitHubRepositoryUseCase interface,
which specifies operations for validating and creating GitHub
repository records.

It acts as a contract for application-level use cases responsible for:
- Validating GitHub repository existence and accessibility
- Persisting GitHub repository records
"""

from abc import ABC, abstractmethod

from backend.src.domain.entities.git_repo import GitRepoCreateDTO, GitRepoDTO


class ICreateGitHubRepositoryUseCase(ABC):
    """
    Define GitHub repository creation behavior required by the application.

    This interface represents the contract for validating and creating
    GitHub repository records while abstracting infrastructure and
    persistence concerns.
    """

    @abstractmethod
    async def execute(self, dto: GitRepoCreateDTO) -> GitRepoDTO:
        """
        Validate and persist a GitHub repository.

        This method:
        - Verifies repository existence and accessibility on GitHub
        - Persists the repository record in the database

        Args:
            dto (GitRepoCreateDTO): Repository creation payload.

        Returns:
            GitRepoDTO: Persisted repository DTO.
        """
        pass