"""Unit tests for GitHubDeploymentAdapter helpers."""

import pytest

from backend.src.domain.exceptions.invalid_github_url_exception import InvalidGitHubUrlException
from backend.src.infrastructure.external.github_deployments import GitHubDeploymentAdapter


def test_parse_repo_rejects_invalid_url() -> None:
    with pytest.raises(InvalidGitHubUrlException):
        GitHubDeploymentAdapter._parse_repo("https://example.com/not-github")


def test_parse_repo_accepts_https_url() -> None:
    owner, repo = GitHubDeploymentAdapter._parse_repo("https://github.com/org/repo")

    assert owner == "org"
    assert repo == "repo"
