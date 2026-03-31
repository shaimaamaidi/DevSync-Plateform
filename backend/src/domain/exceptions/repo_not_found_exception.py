"""
Repository not found exception.

This module defines the RepoNotFoundException, raised when a repository cannot be found.
"""

from backend.src.domain.exceptions.app_exception import AppException


class RepoNotFoundException(AppException):
    """
    Exception raised when a repository cannot be found.

    Attributes:
        message (str): Error message override.
        code (str): Error code.
        http_status (int): HTTP status to return.
    """
    def __init__(self, message="Repository not found with ID/URL/Name."):
        """
        Initialize a repository not found exception.

        Args:
            message (str): Error message (default: "Repository not found with ID/URL/Name.").
        """
        super().__init__(
            message=message,
            code="REPO_NOT_FOUND",
            http_status=404
        )