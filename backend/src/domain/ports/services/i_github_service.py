from abc import ABC, abstractmethod
from typing import List

from backend.src.domain.entities.deployment import DeploymentDTO


class IGitHubService(ABC):
    @abstractmethod
    def get_deployments(self, repo_url: str) -> List[DeploymentDTO]:
        pass

    @abstractmethod
    def display_deployments(self, repo_url: str) -> None:
        pass
