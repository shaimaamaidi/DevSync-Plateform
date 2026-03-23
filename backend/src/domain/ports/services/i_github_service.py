from abc import ABC, abstractmethod
from typing import List
from src.domain.entities.deployment import Deployment


class IGitHubService(ABC):
    @abstractmethod
    def get_deployments(self, repo_url: str) -> List[Deployment]: ...

    @abstractmethod
    def display_deployments(self, repo_url: str) -> None: ...
