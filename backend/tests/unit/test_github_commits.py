"""
Unit tests for GitHub commit adapters.
"""

import pytest

from backend.src.domain.exceptions.github.invalid_github_url_exception import InvalidGitHubUrlException
from backend.src.infrastructure.external.github.base_github_client import BaseGitHubClient
from backend.src.infrastructure.external.github.github_commits import GitHubCommitsAdapter


def test_parse_repo_accepts_https_and_ssh_urls() -> None:
    """
    Test that the base GitHub parser accepts common GitHub URL formats.
    """
    assert BaseGitHubClient._parse_repo("https://github.com/org/repo") == ("org", "repo")
    assert BaseGitHubClient._parse_repo("git@github.com:org/repo.git") == ("org", "repo")


def test_parse_repo_rejects_invalid_url() -> None:
    """
    Test that invalid repository URLs are rejected.
    """
    with pytest.raises(InvalidGitHubUrlException):
        BaseGitHubClient._parse_repo("https://example.com/org/repo")


@pytest.mark.asyncio
async def test_get_commits_deduplicates_and_sorts_results(monkeypatch) -> None:
    """
    Test that commit fetching deduplicates SHAs and sorts by date.
    """
    monkeypatch.setenv("GITHUB_TOKEN", "token")
    monkeypatch.setenv("CONNECT_TIMEOUT", "1")
    monkeypatch.setenv("READ_TIMEOUT", "1")
    monkeypatch.setattr(
        "backend.src.infrastructure.external.github.base_github_client.load_dotenv",
        lambda *args, **kwargs: True,
    )

    adapter = GitHubCommitsAdapter()

    async def fake_github_get(url: str, max_pages: int = 0):
        if "deployments" in url:
            return [{"ref": "main"}, {"ref": "release"}]

        if "sha=main" in url:
            return [
                {
                    "sha": "abcdef123456",
                    "commit": {
                        "message": "Main commit\nBody",
                        "author": {"name": "Alice", "date": "2024-01-02T10:00:00Z"},
                    },
                    "author": {"login": "alice"},
                    "html_url": "https://github.com/org/repo/commit/abcdef1",
                }
            ]

        if "sha=release" in url:
            return [
                {
                    "sha": "abcdef123456",
                    "commit": {
                        "message": "Duplicate commit",
                        "author": {"name": "Alice", "date": "2024-01-02T10:00:00Z"},
                    },
                    "author": {"login": "alice"},
                    "html_url": "https://github.com/org/repo/commit/abcdef1",
                },
                {
                    "sha": "123456abcdef",
                    "commit": {
                        "message": "Release commit",
                        "author": {"name": "Bob", "date": "2024-01-01T10:00:00Z"},
                    },
                    "author": {},
                    "html_url": "https://github.com/org/repo/commit/123456a",
                },
            ]

        raise AssertionError(f"Unexpected GitHub URL: {url}")

    adapter._github_get = fake_github_get  # type: ignore[assignment]

    commits = await adapter.get_commits("https://github.com/org/repo", max_commits=10)

    assert [commit.sha for commit in commits] == ["abcdef1", "123456a"]
    assert commits[0].author == "alice"
    assert commits[1].author == "Bob"
    assert commits[0].date is not None and commits[1].date is not None
    assert commits[0].date >= commits[1].date


@pytest.mark.asyncio
async def test_get_commits_between_dates_filters_and_caps_results(monkeypatch) -> None:
    """
    Test that date-range commit fetching deduplicates and applies the cap.
    """
    monkeypatch.setenv("GITHUB_TOKEN", "token")
    monkeypatch.setenv("CONNECT_TIMEOUT", "1")
    monkeypatch.setenv("READ_TIMEOUT", "1")
    monkeypatch.setattr(
        "backend.src.infrastructure.external.github.base_github_client.load_dotenv",
        lambda *args, **kwargs: True,
    )

    adapter = GitHubCommitsAdapter()

    async def fake_github_get(url: str, max_pages: int = 0):
        if "deployments" in url:
            return [{"ref": "main"}]

        return [
            {
                "sha": "abcdef123456",
                "commit": {
                    "message": "Alpha\nBody",
                    "author": {"name": "Alice", "date": "2024-01-02T10:00:00Z"},
                },
                "author": {"login": "alice"},
                "html_url": "https://github.com/org/repo/commit/abcdef1",
            },
            {
                "sha": "fedcba654321",
                "commit": {
                    "message": "Beta\nBody",
                    "author": {"name": "Bob", "date": "2024-01-01T10:00:00Z"},
                },
                "author": {},
                "html_url": "https://github.com/org/repo/commit/fedcba6",
            },
        ]

    adapter._github_get = fake_github_get  # type: ignore[assignment]

    commits = await adapter.get_commits_between_dates(
        "https://github.com/org/repo",
        since=__import__("datetime").datetime(2024, 1, 1, tzinfo=__import__("datetime").timezone.utc),
        until=__import__("datetime").datetime(2024, 1, 3, tzinfo=__import__("datetime").timezone.utc),
        max_commits=1,
    )

    assert len(commits) == 1
    assert commits[0].sha == "abcdef1"
    assert commits[0].branch == "main"