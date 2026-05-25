"""
Deployment use case module.

This module provides the DeploymentUseCase class, which handles deployment-related queries,
such as listing deployments for a repository.
It coordinates with the GitHub service port and Repository persistence to fetch deployment data.

Classes:
    DeploymentUseCase: Main use case for deployment read operations.
"""

import logging
from typing import List

from backend.src.domain.entities.github.deployment import DeploymentDTO
from backend.src.domain.exceptions.common.invalid_input_exception import InvalidInputException

from backend.src.domain.ports.input.i_deployment_use_case import IDeploymentUseCase
from backend.src.domain.ports.output.github.i_github_deployment_service import IGitHubDeploymentService
from backend.src.domain.ports.repositories.i_repo_repository import IRepoRepository


logger = logging.getLogger(__name__)


class DeploymentUseCase(IDeploymentUseCase):
    """
    Application use case for deployment-related queries, such as listing deployments for a repository.

    Coordinates with the GitHub service port and Repository persistence to fetch deployment data.

    Attributes:
         _repo (IRepoRepository): Repository persistence port.
        _github_deployment_service (IGitHubDeploymentService): GitHub service port.
    """

    def __init__(self, repo_repo: IRepoRepository, github_deployment_service: IGitHubDeploymentService):
        """
        Initialize the use case with a GitHub adapter and repository adapter.

        Args:
            github_deployment_service (IGitHubDeploymentService): GitHub service port.
            repo_repo (IRepoRepository): Repository persistence port.
        """
        self._repo = repo_repo
        self._github_deployment_service = github_deployment_service

    async def list_deployments(self, repo_url: str) -> List[DeploymentDTO]:
        """
        Retrieve deployments associated with a GitHub repository.

        This method first verifies that the repository exists in the local
        database using its URL. If found, it delegates to the GitHub service
        to fetch deployment data from external sources (GitHub Deployments API
        and GitHub Actions).

        Args:
            repo_url (str): GitHub repository URL.

        Returns:
            List[DeploymentDTO]: List of deployment DTOs for the repository.

        Raises:
            InvalidInputException: If repo_url is empty.
        """
        logger.info("Fetching deployments for repository: repo_url=%s.", repo_url)

        if not repo_url:
            logger.warning(
                "Fetching deployments failed: repo_url is empty."
            )
            raise InvalidInputException(
                "Repository URL is required to fetch deployments."
            )

        result = self._repo.find_by_url(repo_url)

        results = await self._github_deployment_service.get_deployments(result.url)

        logger.info(
            "Fetched %s deployments for repository successfully: repo_url=%s.",
            len(results),
            repo_url
        )

        return results
