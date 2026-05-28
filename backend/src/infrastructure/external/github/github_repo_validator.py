"""
GitHub repository existence validation adapter.

This module provides an adapter responsible for validating whether
a GitHub repository exists and is accessible through the GitHub API.

It relies on the shared BaseGitHubClient infrastructure for:
- Repository URL parsing and validation
- Authenticated GitHub API communication
- Error handling and rate limit management

Main classes:
    GitHubRepoValidator
"""

import logging

from backend.src.domain.ports.output.github.i_github_repo_validation_service import IGitHubRepoValidationService
from backend.src.infrastructure.external.github.base_github_client import BaseGitHubClient


logger = logging.getLogger(__name__)


class GitHubRepoValidator(BaseGitHubClient, IGitHubRepoValidationService):
    """
    Adapter responsible for validating GitHub repository existence.

    This class verifies whether a repository:
    - Exists on GitHub
    - Is accessible with the configured authentication token

    It extends BaseGitHubClient to reuse shared GitHub API
    communication and repository parsing logic.
    """

    async def verify_exists(self, url: str) -> bool:
        """
        Verify that a GitHub repository exists and is accessible.

        This method:
        - Parses and validates the repository URL
        - Sends an authenticated request to the GitHub repository endpoint
        - Confirms repository accessibility

        Args:
            url: Full GitHub repository URL.

        Returns:
            True if the repository exists and is accessible.

        Raises:
            InvalidGitHubUrlException: If the repository URL format is invalid.
            GitHubRepoNotFoundException: If the repository does not exist
                or cannot be accessed.
            GitHubRateLimitException: If the GitHub API rate limit is exceeded.
            GitHubApiException: For other GitHub API or network errors.
        """
        owner, repo = self._parse_repo(url)
        api_url = f"https://api.github.com/repos/{owner}/{repo}"

        logger.info(
            "Verifying GitHub repository existence (owner=%s, repo=%s).",
            owner,
            repo,
        )

        await self._github_get(api_url, max_pages=1)

        logger.info(
            "GitHub repository verified successfully (owner=%s, repo=%s).",
            owner,
            repo,
        )

        return True