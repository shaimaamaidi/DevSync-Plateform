"""
ClickUp persistence error exception.

This module defines the ClickUpPersistenceException, raised when an error occurs while accessing
or persisting data related to ClickUp storage operations.
"""

from backend.src.domain.exceptions.base.app_exception import AppException


class ClickUpPersistenceException(AppException):
    """
    Exception raised when ClickUp storage or persistence operations fail.

    This exception is used to indicate failures occurring during interaction with ClickUp data storage,
    such as read/write errors, connectivity issues, or unexpected API behavior.

    Attributes:
        message (str): Human-readable error message describing the persistence failure.
        code (str): Internal error code identifying the type of ClickUp persistence error.
        http_status (int): HTTP status code returned to the client.
    """

    def __init__(self, message: str = "Something went wrong. Please try again."):
        """
        Initialize a ClickUp persistence exception.

        Args:
            message (str): Error message describing the persistence failure.
        """
        super().__init__(
            message=message,
            code="CLICKUP_PERSISTENCE_ERROR",
            http_status=500,
        )