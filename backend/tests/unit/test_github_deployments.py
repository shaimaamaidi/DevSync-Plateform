"""
Unit tests for GitHubDeploymentAdapter helpers.
"""

import pytest

from backend.src.domain.exceptions.invalid_github_url_exception import InvalidGitHubUrlException
from backend.src.infrastructure.external.github_deployments import GitHubDeploymentAdapter


def test_parse_repo_rejects_invalid_url() -> None:
    """
    Test that _parse_repo raises InvalidGitHubUrlException for a non-GitHub URL.
    """
    with pytest.raises(InvalidGitHubUrlException):
        GitHubDeploymentAdapter._parse_repo("https://example.com/not-github")


def test_parse_repo_accepts_https_url() -> None:
    """
    Test that _parse_repo correctly parses a valid GitHub HTTPS URL.
    """
    owner, repo = GitHubDeploymentAdapter._parse_repo("https://github.com/org/repo")

    assert owner == "org"
    assert repo == "repo"
