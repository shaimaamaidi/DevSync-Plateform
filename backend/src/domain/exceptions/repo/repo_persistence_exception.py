"""
Repository persistence exception.

This module defines the RepoPersistenceException, raised when an error occurs during
repository persistence operations such as database access, retrieval, or storage failures.
"""

from backend.src.domain.exceptions.base.app_exception import AppException


class RepoPersistenceException(AppException):
    """
    Exception raised when repository persistence operations fail.

    This exception is used to indicate failures occurring while accessing or manipulating
    repository data in the persistence layer, such as database errors or repository access issues.

    Attributes:
        message (str): Human-readable error message describing the persistence failure.
        code (str): Internal error code identifying the repository persistence error.
        http_status (int): HTTP status code returned to the client.
    """

    def __init__(self, message: str = "Error occurred while accessing repository data."):
        """
        Initialize a RepoPersistenceException.

        Args:
            message (str): Error message describing the persistence failure
                (default: "Error occurred while accessing repository data.").
        """
        super().__init__(
            message=message,
            code="REPO_PERSISTENCE_ERROR",
            http_status=500,
        )