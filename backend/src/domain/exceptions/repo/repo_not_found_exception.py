"""
Repository not found exception.

This module defines the RepoNotFoundException, raised when a repository cannot be found
using the provided identifier such as ID, URL, or name.
"""

from backend.src.domain.exceptions.base.app_exception import AppException


class RepoNotFoundException(AppException):
    """
    Exception raised when a repository cannot be found.

    This exception is used when a repository lookup operation fails because the requested
    repository does not exist or cannot be retrieved using the given identifier.

    Attributes:
        message (str): Human-readable error message describing the missing repository.
        code (str): Internal error code identifying the repository not found error.
        http_status (int): HTTP status code returned to the client.
    """

    def __init__(self, message: str = "Repository not found with ID/URL/Name."):
        """
        Initialize a RepoNotFoundException.

        Args:
            message (str): Error message describing the missing repository
                (default: "Repository not found with ID/URL/Name.").
        """
        super().__init__(
            message=message,
            code="REPO_NOT_FOUND",
            http_status=404,
        )