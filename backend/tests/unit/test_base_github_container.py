"""
Unit tests for BaseGitHubContainer.
"""

from unittest.mock import MagicMock

import pytest

from backend.src.domain.exceptions.base.app_exception import AppException
from backend.src.infrastructure.di import base_github_container
from backend.src.infrastructure.di.base_github_container import BaseGitHubContainer


def test_base_github_container_initializes_git_services(monkeypatch) -> None:
    """
    Test that the GitHub container wires the deployment and commit adapters.
    """
    deployment_service = MagicMock(name="deployment_service")
    commit_service = MagicMock(name="commit_service")

    monkeypatch.setattr(base_github_container, "GitHubDeploymentAdapter", lambda: deployment_service)
    monkeypatch.setattr(base_github_container, "GitHubCommitsAdapter", lambda: commit_service)

    container = BaseGitHubContainer()

    assert container.github_deployment_service is deployment_service
    assert container.github_commit_service is commit_service


def test_base_github_container_wraps_initialization_failure(monkeypatch) -> None:
    """
    Test that the GitHub container raises an application error when initialization fails.
    """
    monkeypatch.setattr(base_github_container, "GitHubDeploymentAdapter", lambda: (_ for _ in ()).throw(RuntimeError("boom")))

    with pytest.raises(AppException):
        BaseGitHubContainer()