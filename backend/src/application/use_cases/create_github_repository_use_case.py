"""
GitHub repository creation use case module.

This module provides the CreateRepoUseCase class, which is responsible
for validating and persisting GitHub repository records.

The use case verifies repository existence and accessibility through
the GitHub API before delegating persistence to the repository port.

Classes:
    CreateRepoUseCase: Use case for validating and creating GitHub repository records.
"""

import logging

from backend.src.domain.entities.git_repo import GitRepoCreateDTO, GitRepoDTO
from backend.src.domain.ports.input.i_create_github_repository_use_case import ICreateGitHubRepositoryUseCase
from backend.src.domain.ports.output.github.i_github_repo_validation_service import (
    IGitHubRepoValidationService,
)
from backend.src.domain.ports.repositories.i_repo_repository import IRepoRepository


logger = logging.getLogger(__name__)


class CreateGitHubRepositoryUseCase(ICreateGitHubRepositoryUseCase):
    """
    Application use case for creating GitHub repository records.

    This class validates the existence and accessibility of a GitHub
    repository before persisting it through the repository port.

    Attributes:
        _repo_repository (IRepoRepository): Port used for repository persistence.
        _validator (IGitHubRepoValidationService): Port used for GitHub repository validation.
    """

    def __init__(
        self,
        repo_repository: IRepoRepository,
        validator: IGitHubRepoValidationService,
    ):
        """
        Initialize the use case with required ports.

        Args:
            repo_repository (IRepoRepository): Repository persistence port.
            validator (IGitHubRepoValidationService): GitHub repository validation port.
        """
        self._repo_repository = repo_repository
        self._validator = validator

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

        Raises:
            InvalidGitHubUrlException: If the repository URL format is invalid.
            GitHubRepoNotFoundException: If the repository does not exist
                or is inaccessible.
            GitHubRateLimitException: If the GitHub API rate limit is exceeded.
            GitHubApiException: For other GitHub API or network errors.
            InvalidInputException: If the repository URL already exists.
            RepoPersistenceException: If repository persistence fails.
        """
        logger.info("Validating GitHub repository before creation. url=%s.", dto.url)

        await self._validator.verify_exists(dto.url)

        logger.info(
            "GitHub repository verified successfully. Persisting repository. url=%s.",
            dto.url,
        )

        result = self._repo_repository.save(dto)

        logger.info(
            "GitHub repository created successfully. repo_id=%s.",
            result.id,
        )

        return result