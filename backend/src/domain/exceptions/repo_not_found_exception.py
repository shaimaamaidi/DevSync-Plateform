"""
Repository not found exception.

This module defines the RepoNotFoundException, raised when a repository cannot be found.
"""

from backend.src.domain.exceptions.app_exception import AppException


class RepoNotFoundException(AppException):
    """
    Exception raised when a repository cannot be found.

    Args:
        message: Error message override.
    """
    def __init__(self, message=f"Repository not found with ID/URL/Name"):
        """Initialize a repository not found exception.

        Args:
            message: Error message override.
        """
        super().__init__(
            message=message,
            code="REPO_NOT_FOUND",
            http_status=404
        )