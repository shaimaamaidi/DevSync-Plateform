"""
Repository persistence exception.

This module defines the RepoPersistenceException, raised when repository persistence operations fail.
"""

from backend.src.domain.exceptions.app_exception import AppException


class RepoPersistenceException(AppException):
    """
    Exception raised when repository persistence fails.

    Args:
        msg: Error message override.
    """
    def __init__(self, msg: str = "Error occurred while accessing repository data"):
        """Initialize a repository persistence exception.

        Args:
            msg: Error message override.
        """
        super().__init__(
            message=msg,
            code="REPO_PERSISTENCE_ERROR",
            http_status=500
        )