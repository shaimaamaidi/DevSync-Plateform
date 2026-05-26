"""
Unit tests for GitHubDeploymentAdapter helpers.
"""

from datetime import datetime, timezone

import pytest

from backend.src.domain.entities.github.deployment import DeploymentDTO
from backend.src.domain.exceptions.common.missing_env_variable_exception import MissingEnvVariableException
from backend.src.domain.exceptions.github.invalid_github_url_exception import InvalidGitHubUrlException
from backend.src.infrastructure.external.github.github_deployments import GitHubDeploymentAdapter


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


def test_github_deployment_adapter_initializes_from_environment(monkeypatch) -> None:
    """
    Test that the deployment adapter reads GitHub and deployment limits from the environment.
    """
    monkeypatch.setattr("backend.src.infrastructure.external.github.github_deployments.load_dotenv", lambda *args, **kwargs: True)
    monkeypatch.setenv("GITHUB_TOKEN", "gh-token")
    monkeypatch.setenv("CONNECT_TIMEOUT", "3")
    monkeypatch.setenv("READ_TIMEOUT", "7")
    monkeypatch.setenv("ACTIONS_MAX_RUNS", "8")
    monkeypatch.setenv("DEPLOYMENTS_MAX_ITEMS", "9")

    adapter = GitHubDeploymentAdapter()

    assert adapter.GITHUB_TOKEN == "gh-token"
    assert adapter.ACTIONS_MAX_RUNS == 8
    assert adapter.DEPLOYMENTS_MAX_ITEMS == 9


def test_github_deployment_adapter_raises_when_token_is_missing(monkeypatch) -> None:
    """
    Test that the deployment adapter raises when GitHub token configuration is missing.
    """
    monkeypatch.setattr("backend.src.infrastructure.external.github.base_github_client.load_dotenv", lambda *args, **kwargs: True)

    def fake_getenv(key, default=None):
        if key == "GITHUB_TOKEN":
            return None
        if key in {"CONNECT_TIMEOUT", "READ_TIMEOUT"}:
            return "1"
        return default

    monkeypatch.setattr("backend.src.infrastructure.external.github.base_github_client.os.getenv", fake_getenv)

    with pytest.raises(MissingEnvVariableException):
        GitHubDeploymentAdapter()


def test_is_deploy_workflow_filters_keywords() -> None:
    """
    Test that deploy-like workflow names are accepted and unrelated names are rejected.
    """
    assert GitHubDeploymentAdapter._is_deploy_workflow("Deploy to staging") is True
    assert GitHubDeploymentAdapter._is_deploy_workflow("Build and test") is False


@pytest.mark.asyncio
async def test_get_deployments_merges_and_limits_results(monkeypatch) -> None:
    """
    Test that deployment fetching merges sources, deduplicates, and applies the limit.
    """
    monkeypatch.setattr("backend.src.infrastructure.external.github.github_deployments.load_dotenv", lambda *args, **kwargs: True)
    monkeypatch.setenv("GITHUB_TOKEN", "gh-token")
    monkeypatch.setenv("CONNECT_TIMEOUT", "1")
    monkeypatch.setenv("READ_TIMEOUT", "1")
    monkeypatch.setenv("ACTIONS_MAX_RUNS", "5")
    monkeypatch.setenv("DEPLOYMENTS_MAX_ITEMS", "2")

    adapter = GitHubDeploymentAdapter()

    async def fake_fetch_api(owner: str, repo: str, max_deployments: int | None):
        return [
            DeploymentDTO(
                dep_id=1,
                environment="prod",
                ref="main",
                sha="abc1234",
                creator="alice",
                created_at=datetime(2024, 1, 2, tzinfo=timezone.utc),
                description="api",
                state="success",
                log_url="https://example.com/api",
            )
        ]

    async def fake_fetch_actions(owner: str, repo: str):
        return [
            DeploymentDTO(
                dep_id=1,
                environment="prod",
                ref="main",
                sha="abc1234",
                creator="alice",
                created_at=datetime(2024, 1, 2, tzinfo=timezone.utc),
                description="duplicate",
                state="success",
                log_url="https://example.com/actions",
            ),
            DeploymentDTO(
                dep_id=2,
                environment="staging",
                ref="dev",
                sha="def5678",
                creator="bob",
                created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
                description="actions",
                state="success",
                log_url="https://example.com/actions-2",
            ),
        ]

    monkeypatch.setattr(adapter, "_fetch_deployments_from_api", fake_fetch_api)
    monkeypatch.setattr(adapter, "_fetch_deployments_from_actions", fake_fetch_actions)

    result = await adapter.get_deployments("https://github.com/org/repo", max_deployments=None)

    assert [deployment.dep_id for deployment in result] == [1, 2]
    assert len(result) == 2
