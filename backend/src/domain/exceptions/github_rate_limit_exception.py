"""
GitHub rate limit exception.

This module defines the GitHubRateLimitException, raised when the GitHub API rate limit
is exceeded and further requests are temporarily blocked.
"""

from backend.src.domain.exceptions.app_exception import AppException


class GitHubRateLimitException(AppException):
    """
    Exception raised when GitHub API rate limit is exceeded.

    This exception is used when the application exceeds the allowed number of requests
    to the GitHub API within a given time window. It may include the reset time indicating
    when requests can be retried.

    Attributes:
        message (str): Human-readable error message describing the rate limit issue.
        code (str): Internal error code identifying the GitHub rate limit error.
        http_status (int): HTTP status code returned to the client.
    """

    def __init__(self, reset_time: str = None):
        """
        Initialize a GitHubRateLimitException.

        Args:
            reset_time (str, optional): UTC reset time from GitHub response headers indicating
                when the rate limit will reset.
        """
        msg = "GitHub API rate limit exceeded."
        if reset_time:
            msg += f" Please retry after {reset_time} UTC."

        super().__init__(
            message=msg,
            code="GITHUB_RATE_LIMIT",
            http_status=429,
        )