"""
Service port for deployment operations.

This module defines the IDeploymentService interface, which specifies operations
related to retrieving deployment information for GitHub repositories.

It acts as a contract for application-level services responsible for:
- Validating repository existence
- Coordinating with GitHub integration services
- Aggregating deployment data from external sources
"""

from abc import ABC, abstractmethod
from typing import List

from backend.src.domain.entities.deployment import DeploymentDTO


class IDeploymentUseCase(ABC):
    """
    Define deployment service behavior required by the application.

    This interface represents the contract for retrieving deployment information
    associated with GitHub repositories. It abstracts repository validation and
    external GitHub data aggregation.
    """

    @abstractmethod
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
        pass
