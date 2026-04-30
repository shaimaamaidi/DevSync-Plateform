"""
Service port for GitHub integrations.

This module defines the IGitHubService interface, which specifies operations for interacting
with GitHub, such as fetching deployments and other repository-related data.
"""

from abc import ABC, abstractmethod
from typing import List

from backend.src.domain.entities.deployment import DeploymentDTO


class IGitHubService(ABC):
    """
    Define GitHub service behavior required by the application.

    This interface represents the contract for interacting with GitHub APIs in order to
    retrieve repository-related information such as deployments.
    """

    @abstractmethod
    async def get_deployments(self, repo_url: str) -> List[DeploymentDTO]:
        """
        Fetch deployments for a GitHub repository.

        Args:
            repo_url (str): GitHub repository URL.

        Returns:
            List[DeploymentDTO]: List of deployment data transfer objects.
        """
        pass