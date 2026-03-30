"""
Deployment service module.

This module provides the DeploymentService class, which handles deployment-related queries, such as listing deployments for a repository.
It coordinates with the GitHub service port to fetch deployment data.

Classes:
    DeploymentService: Main service for deployment read operations.
"""

import logging
from typing import List

from backend.src.domain.entities.deployment import DeploymentDTO
from backend.src.domain.ports.services.i_github_service import IGitHubService


logger = logging.getLogger(__name__)


class DeploymentService:
    """
    Application service for deployment-related queries, such as listing deployments for a repository.

    Coordinates with the GitHub service port to fetch deployment data.

    Attributes:
        _github (IGitHubService): GitHub service port.
    """
    def __init__(self, github_service: IGitHubService):
        """
        Initialize the service with a GitHub adapter.

        Args:
            github_service (IGitHubService): GitHub service port.
        """
        self._github = github_service

    def list_deployments(self, repo_url: str) -> List[DeploymentDTO]:
        """
        List deployments for a repository URL.

        Args:
            repo_url (str): GitHub repository URL.

        Returns:
            List[DeploymentDTO]: List of deployment DTOs for the repository.
        """
        logger.info("Fetching deployments for repository: repo_url=%s.", repo_url)
        
        results = self._github.get_deployments(repo_url)

        logger.info(
            "Fetched %s deployments for repository successfully: repo_url=%s.",
            len(results),
            repo_url
        )
        
        return results
