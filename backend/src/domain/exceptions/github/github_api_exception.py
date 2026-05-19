"""
GitHub API exception.

This module defines the GitHubApiException, raised when an error occurs during communication
with the GitHub API, such as request failures, authentication issues, or service unavailability.
"""

from backend.src.domain.exceptions.base.app_exception import AppException


class GitHubApiException(AppException):
    """
    Exception raised when a GitHub API request fails.

    This exception is used to signal errors occurring during interactions with the GitHub API,
    including network issues, invalid responses, authentication failures, or rate limiting.

    Attributes:
        message (str): Human-readable error message describing the API failure.
        code (str): Stable error code identifying the GitHub API error type.
        http_status (int): HTTP status code returned to the client.
    """

    def __init__(self, message: str = "Unable to reach GitHub. Please try again later."):
        """
        Initialize a GitHubApiException.

        Args:
            message (str): Human-readable error message.
        """
        super().__init__(
            message=message,
            code="GITHUB_API_ERROR",
            http_status=502
        )