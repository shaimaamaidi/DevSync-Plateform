"""
Repository persistence exception.

This module defines the RepoPersistenceException, raised when repository persistence operations fail.
"""

from backend.src.domain.exceptions.app_exception import AppException


class RepoPersistenceException(AppException):
    """
    Exception raised when repository persistence fails.

    Attributes:
        message (str): Error message override.
        code (str): Error code.
        http_status (int): HTTP status to return.
    """
    def __init__(self, message: str = "Error occurred while accessing repository data."):
        """
        Initialize a repository persistence exception.

        Args:
            message (str): Error message (default: "Error occurred while accessing repository data.").
        """
        super().__init__(
            message=message,
            code="REPO_PERSISTENCE_ERROR",
            http_status=500
        )