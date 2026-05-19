"""
GitHub repository not found exception.

This module defines the GitHubRepoNotFoundException, raised when a GitHub repository
cannot be found or is inaccessible via the GitHub API.
"""

from backend.src.domain.exceptions.base.app_exception import AppException


class GitHubRepoNotFoundException(AppException):
    """
    Exception raised when a GitHub repository cannot be found.

    This exception is used when the requested repository does not exist, is private,
    or cannot be retrieved from the GitHub API using the provided URL or identifier.

    Attributes:
        message (str): Human-readable error message describing the missing repository.
        code (str): Internal error code identifying the repository not found error.
        http_status (int): HTTP status code returned to the client.
    """

    def __init__(self):
        """
        Initialize a GitHubRepoNotFoundException.
        """
        super().__init__(
            message="The requested repository could not be found. Please check the URL and try again.",
            code="GITHUB_REPO_NOT_FOUND",
            http_status=404,
        )