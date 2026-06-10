"""
Base adapter for GitHub API communication.

This module provides a shared base implementation for all GitHub adapters.
It centralizes authentication, HTTP configuration, pagination handling,
error management, and repository URL parsing for consistent GitHub API access.
"""

import logging
import re
from datetime import datetime, timezone

import asyncio
import httpx

from backend.src.domain.exceptions.github.github_api_exception import GitHubApiException
from backend.src.domain.exceptions.github.github_rate_limit_exception import GitHubRateLimitException
from backend.src.domain.exceptions.github.github_repo_not_found_exception import GitHubRepoNotFoundException
from backend.src.domain.exceptions.github.invalid_github_url_exception import InvalidGitHubUrlException
from backend.src.infrastructure.config.settings import settings


logger = logging.getLogger(__name__)


class BaseGitHubClient:
    """
    Base adapter for GitHub API communication.

    This class provides shared infrastructure for GitHub adapters, including:
    - Authentication via GitHub token
    - HTTP client timeout configuration
    - Paginated request handling
    - Repository URL parsing and validation

    It serves as the foundation for all GitHub-related adapters in the system.
    """

    def __init__(self):
        """
        Initialize the GitHub base client.

        This constructor:
        - Loads environment variables from .env file if available
        - Reads HTTP timeout configuration (connect/read)
        - Validates the presence of the GitHub authentication token
        - Configures the HTTP timeout settings for API requests
        """

        connect_timeout = settings.CONNECT_TIMEOUT
        read_timeout = settings.READ_TIMEOUT


        self.GITHUB_TIMEOUT = httpx.Timeout(
            connect=connect_timeout,
            read=read_timeout,
            write=read_timeout,
            pool=connect_timeout,
        )

        self.GITHUB_TOKEN = settings.GITHUB_TOKEN

    @staticmethod
    def _parse_repo(url: str) -> tuple[str, str]:
        """
        Parse a GitHub repository URL into (owner, repo).

        Args:
            url: Full GitHub repository URL.

        Returns:
            Tuple of (owner, repo name).

        Raises:
            InvalidGitHubUrlException: If the URL format is invalid.
        """
        url = url.rstrip("/")
        match = re.search(r"github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?$", url)

        if not match:
            logger.warning("Invalid GitHub repository URL: %s.", url)
            raise InvalidGitHubUrlException()

        owner, repo = match.group(1), match.group(2)
        logger.info("Parsed owner=%s, repo=%s.", owner, repo)

        return owner, repo

    def _get_headers(self) -> dict:
        return {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Authorization": f"token {self.GITHUB_TOKEN}",
        }

    async def _github_get(self, url: str, max_pages: int = 0) -> list[dict]:
        """
        Perform an authenticated paginated GET request to the GitHub API.

        Args:
            url: GitHub API endpoint URL.
            max_pages: Maximum pages to fetch (0 = unlimited).

        Returns:
            Aggregated list of results.

        Raises:
            GitHubRepoNotFoundException: If resource returns 404.
            GitHubRateLimitException: If rate limit is exceeded.
            GitHubApiException: For other HTTP or network errors.
        """
        results = []
        page_count = 0
        MAX_RETRIES = 3

        async with httpx.AsyncClient(timeout=self.GITHUB_TIMEOUT) as client:
            while url:
                if max_pages and page_count >= max_pages:
                    break

                page_count += 1
                retries = 0

                while retries <= MAX_RETRIES:
                    try:
                        resp = await client.get(url, headers=self._get_headers())
                        resp.raise_for_status()
                        break
                    except httpx.HTTPStatusError as e:
                        if e.response.status_code == 404:
                            raise GitHubRepoNotFoundException()
                        if e.response.status_code == 403:
                            reset = e.response.headers.get("X-RateLimit-Reset")
                            if reset:
                                wait = max(int(reset) - int(datetime.now(timezone.utc).timestamp()), 1)
                                await asyncio.sleep(wait)
                                retries += 1
                                if retries > MAX_RETRIES:
                                    raise GitHubRateLimitException() from e
                                continue
                        raise GitHubApiException() from e
                    except httpx.RequestError as e:
                        raise GitHubApiException() from e

                data = resp.json()

                if isinstance(data, list):
                    results.extend(data)
                else:
                    results.append(data)

                link = resp.headers.get("Link", "")
                url = None
                for part in link.split(","):
                    if 'rel="next"' in part:
                        m = re.search(r"<([^>]+)>", part)
                        if m:
                            url = m.group(1)
                        break

        return results