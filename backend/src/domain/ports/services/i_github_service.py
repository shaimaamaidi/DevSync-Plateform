"""Service port for GitHub integrations."""

from abc import ABC, abstractmethod
from typing import List

from backend.src.domain.entities.deployment import DeploymentDTO


class IGitHubService(ABC):
    """Define GitHub service behavior required by the application."""
    @abstractmethod
    def get_deployments(self, repo_url: str) -> List[DeploymentDTO]:
        """Fetch deployments for a repository URL.

        Args:
            repo_url: GitHub repository URL.

        Returns:
            List of deployment DTOs.
        """
        pass
    
        
