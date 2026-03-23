from typing import List
from src.domain.entities.deployment import Deployment
from src.domain.ports.services.i_github_service import IGitHubService


class DeploymentService:
    def __init__(self, github_service: IGitHubService):
        self._github = github_service

    def list_deployments(self, repo_url: str) -> List[Deployment]:
        return self._github.get_deployments(repo_url)

    def display(self, repo_url: str) -> None:
        self._github.display_deployments(repo_url)