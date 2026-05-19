"""
GitHub rate limit exception.

This module defines the GitHubRateLimitException, raised when the GitHub API rate limit
is exceeded and further requests are temporarily blocked.
"""

from backend.src.domain.exceptions.base.app_exception import AppException


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

    def __init__(self):
        """
        Initialize a GitHubRateLimitException.
        """
        super().__init__(
            message="GitHub service is temporarily unavailable. Please try again later.",
            code="GITHUB_RATE_LIMIT",
            http_status=429,
        )