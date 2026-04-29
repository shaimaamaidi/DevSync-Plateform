"""
Deployment use case module.

This module provides the DeploymentUseCase class, which handles deployment-related queries, such as listing deployments for a repository.
It coordinates with the GitHub service port and Repository persistence to fetch deployment data.

Classes:
    DeploymentUseCase: Main use case for deployment read operations.
"""

import logging
from typing import List

from backend.src.domain.entities.deployment import DeploymentDTO

from backend.src.domain.ports.input.i_deployment_use_case import IDeploymentUseCase
from backend.src.domain.ports.repositories.i_repo_repository import IRepoRepository
from backend.src.domain.ports.services.i_github_service import IGitHubService

logger = logging.getLogger(__name__)


class DeploymentUseCase(IDeploymentUseCase):
    """
    Application use case for deployment-related queries, such as listing deployments for a repository.

    Coordinates with the GitHub service port and Repository persistence to fetch deployment data.

    Attributes:
         _repo (IRepoRepository): Repository persistence port.
        _github (IGitHubService): GitHub service port.
    """

    def __init__(self, repo_repo: IRepoRepository, github_service: IGitHubService):
        """
        Initialize the use case with a GitHub adapter and repository adapter.

        Args:
            github_service (IGitHubService): GitHub service port.
            repo_repo (IRepoRepository): Repository persistence port.
        """
        self._repo = repo_repo
        self._github = github_service

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
        """
        logger.info("Fetching deployments for repository: repo_url=%s.", repo_url)

        result = self._repo.find_by_url(repo_url)

        results = await self._github.get_deployments(result.url)

        logger.info(
            "Fetched %s deployments for repository successfully: repo_url=%s.",
            len(results),
            repo_url
        )

        return results
