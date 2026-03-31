"""
GitHub rate limit exception.

This module defines the GitHubRateLimitException, raised when the GitHub API rate limit is exceeded.
"""

from backend.src.domain.exceptions.app_exception import AppException


class GitHubRateLimitException(AppException):
    """
    Exception raised when GitHub API rate limit is exceeded.

    Attributes:
        message (str): Error message override.
        code (str): Error code.
        http_status (int): HTTP status to return.
    """
    def __init__(self, reset_time: str = None):
        """
        Initialize a GitHub rate limit exception.

        Args:
            reset_time (str): UTC reset time from GitHub headers.
        """
        msg = "GitHub API rate limit exceeded."
        if reset_time:
            msg += f" Please retry after {reset_time} UTC."
        super().__init__(
            message=msg,
            code="GITHUB_RATE_LIMIT",
            http_status=429
        )