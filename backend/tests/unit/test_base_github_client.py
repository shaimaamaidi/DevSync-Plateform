"""
Unit tests for BaseGitHubClient.
"""

from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
import httpx

from backend.src.domain.exceptions.common.missing_env_variable_exception import MissingEnvVariableException
from backend.src.domain.exceptions.github.github_api_exception import GitHubApiException
from backend.src.domain.exceptions.github.github_rate_limit_exception import GitHubRateLimitException
from backend.src.domain.exceptions.github.github_repo_not_found_exception import GitHubRepoNotFoundException
from backend.src.domain.exceptions.github.invalid_github_url_exception import InvalidGitHubUrlException
from backend.src.infrastructure.external.github.base_github_client import BaseGitHubClient


def test_base_github_client_initializes_from_environment(monkeypatch) -> None:
    """
    Test that the GitHub client reads token and timeout configuration from the environment.
    """
    monkeypatch.setattr("backend.src.infrastructure.external.github.base_github_client.load_dotenv", lambda *args, **kwargs: True)
    monkeypatch.setenv("GITHUB_TOKEN", "gh-token")
    monkeypatch.setenv("CONNECT_TIMEOUT", "3")
    monkeypatch.setenv("READ_TIMEOUT", "7")

    client = BaseGitHubClient()

    assert client.GITHUB_TOKEN == "gh-token"
    assert client.GITHUB_TIMEOUT.connect == 3
    assert client.GITHUB_TIMEOUT.read == 7


def test_base_github_client_raises_when_token_is_missing(monkeypatch) -> None:
    """
    Test that the GitHub client raises when the token is not configured.
    """
    monkeypatch.setattr("backend.src.infrastructure.external.github.base_github_client.load_dotenv", lambda *args, **kwargs: True)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)

    with pytest.raises(MissingEnvVariableException):
        BaseGitHubClient()


def test_parse_repo_supports_https_ssh_and_git_suffix() -> None:
    """
    Test that repo URLs are parsed consistently across supported formats.
    """
    assert BaseGitHubClient._parse_repo("https://github.com/org/repo") == ("org", "repo")
    assert BaseGitHubClient._parse_repo("git@github.com:org/repo.git") == ("org", "repo")


def test_parse_repo_raises_for_invalid_url() -> None:
    """
    Test that invalid GitHub URLs are rejected.
    """
    with pytest.raises(InvalidGitHubUrlException):
        BaseGitHubClient._parse_repo("https://example.com/org/repo")


@pytest.mark.asyncio
async def test_github_get_paginates_and_flattens_list(monkeypatch) -> None:
    """
    Test that _github_get follows pagination links and aggregates list responses.
    """
    monkeypatch.setattr("backend.src.infrastructure.external.github.base_github_client.load_dotenv", lambda *args, **kwargs: True)
    monkeypatch.setenv("GITHUB_TOKEN", "gh-token")

    client = BaseGitHubClient()

    class FakeResponse:
        def __init__(self, payload, headers=None) -> None:
            self._payload = payload
            self.headers = headers or {}

        def raise_for_status(self) -> None:
            return None

        def json(self):
            return self._payload

    class FakeAsyncClient:
        def __init__(self, *args, **kwargs) -> None:
            self.calls = []

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, url, headers):
            self.calls.append(url)
            if url.endswith("page=1"):
                return FakeResponse([{"id": 1}], {"Link": '<https://api.github.com/resource?page=2>; rel="next"'})
            return FakeResponse([{"id": 2}])

    monkeypatch.setattr(httpx, "AsyncClient", FakeAsyncClient)

    results = await client._github_get("https://api.github.com/resource?page=1")

    assert results == [{"id": 1}, {"id": 2}]


@pytest.mark.asyncio
async def test_github_get_raises_repo_not_found_on_404(monkeypatch) -> None:
    """
    Test that a 404 response raises the repository-not-found exception.
    """
    monkeypatch.setattr("backend.src.infrastructure.external.github.base_github_client.load_dotenv", lambda *args, **kwargs: True)
    monkeypatch.setenv("GITHUB_TOKEN", "gh-token")

    client = BaseGitHubClient()

    class FakeHTTPStatusError(httpx.HTTPStatusError):
        def __init__(self):
            request = httpx.Request("GET", "https://api.github.com/resource")
            response = httpx.Response(404, request=request)
            super().__init__("not found", request=request, response=response)

    class FakeResponse:
        headers = {}

        def raise_for_status(self) -> None:
            raise FakeHTTPStatusError()

    class FakeAsyncClient:
        def __init__(self, *args, **kwargs) -> None:
            self.calls = []

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, url, headers):
            return FakeResponse()

    monkeypatch.setattr(httpx, "AsyncClient", FakeAsyncClient)

    with pytest.raises(GitHubRepoNotFoundException):
        await client._github_get("https://api.github.com/resource")


@pytest.mark.asyncio
async def test_github_get_raises_api_exception_on_request_error(monkeypatch) -> None:
    """
    Test that network errors are normalized to a GitHub API exception.
    """
    monkeypatch.setattr("backend.src.infrastructure.external.github.base_github_client.load_dotenv", lambda *args, **kwargs: True)
    monkeypatch.setenv("GITHUB_TOKEN", "gh-token")

    client = BaseGitHubClient()

    class FakeAsyncClient:
        def __init__(self, *args, **kwargs) -> None:
            self.calls = []

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, url, headers):
            request = httpx.Request("GET", url)
            raise httpx.RequestError("network down", request=request)

    monkeypatch.setattr(httpx, "AsyncClient", FakeAsyncClient)

    with pytest.raises(GitHubApiException):
        await client._github_get("https://api.github.com/resource")