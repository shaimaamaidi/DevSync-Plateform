"""
Unit tests for DeploymentContainer.
"""

from unittest.mock import MagicMock

from backend.src.application.use_cases.deployment_use_case import DeploymentUseCase
from backend.src.infrastructure.di import deployment_container
from backend.src.infrastructure.di.deployment_container import DeploymentContainer


def test_deployment_container_initializes_base_github_dependencies(monkeypatch) -> None:
    """
    Test that the deployment container wires the GitHub base dependencies.
    """
    github_service = MagicMock(name="github_service")
    commit_service = MagicMock(name="commit_service")

    def fake_base_init(self) -> None:
        self.github_deployment_service = github_service
        self.github_commit_service = commit_service

    monkeypatch.setattr(deployment_container.BaseGitHubContainer, "__init__", fake_base_init)

    container = DeploymentContainer()

    assert container.github_deployment_service is github_service
    assert container.github_commit_service is commit_service


def test_deployment_container_creates_deployment_use_case(monkeypatch) -> None:
    """
    Test that the deployment container builds the deployment use case with the GitHub service.
    """
    github_service = MagicMock(name="github_service")

    def fake_base_init(self) -> None:
        self.github_deployment_service = github_service
        self.github_commit_service = MagicMock(name="commit_service")

    monkeypatch.setattr(deployment_container.BaseGitHubContainer, "__init__", fake_base_init)

    container = DeploymentContainer()
    repo_repository = MagicMock()

    use_case = container.create_deployment_use_case(repo_repository)

    assert isinstance(use_case, DeploymentUseCase)
    assert use_case._repo is repo_repository
    assert use_case._github_deployment_service is github_service