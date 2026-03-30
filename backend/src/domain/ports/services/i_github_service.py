"""
Service port for GitHub integrations.

This module defines the IGitHubService interface, which specifies operations for interacting with GitHub, such as fetching deployments.
"""

from abc import ABC, abstractmethod
from typing import List

from backend.src.domain.entities.deployment import DeploymentDTO


class IGitHubService(ABC):
    """
    Define GitHub service behavior required by the application.
    """
    @abstractmethod
    def get_deployments(self, repo_url: str) -> List[DeploymentDTO]:
        """Fetch deployments for a repository URL.

        Args:
            repo_url: GitHub repository URL.

        Returns:
            List of deployment DTOs.
        """
        pass
    
        
