"""Application service for deployment queries."""

import logging
from typing import List

from backend.src.domain.entities.deployment import DeploymentDTO
from backend.src.domain.ports.services.i_github_service import IGitHubService


logger = logging.getLogger(__name__)


class DeploymentService:
    """Provide deployment read use cases."""
    def __init__(self, github_service: IGitHubService):
        """Initialize the service with a GitHub adapter.

        Args:
            github_service: GitHub service port.
        """
        self._github = github_service

    def list_deployments(self, repo_url: str) -> List[DeploymentDTO]:
        """List deployments for a repository URL.

        Args:
            repo_url: GitHub repository URL.

        Returns:
            Deployment DTO list.
        """
        logger.info("Fetching deployments for repository: repo_url=%s.", repo_url)
        
        results = self._github.get_deployments(repo_url)

        logger.info(
            "Fetched %s deployments for repository successfully: repo_url=%s.",
            len(results),
            repo_url
        )
        
        return results
