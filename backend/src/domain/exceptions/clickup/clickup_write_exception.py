"""
ClickUp write exception.

This module defines the ClickUpWriteException, a generic exception used
to handle failures that occur during write operations in ClickUp
(create, update, delete).
"""

from backend.src.domain.exceptions.base.app_exception import AppException


class ClickUpWriteException(AppException):
    """
    Generic exception for ClickUp write operations.

    This exception is raised when an error occurs while attempting to
    create, update, or delete resources in ClickUp (Spaces, Folders,
    Lists, Tasks, Statuses, etc.).

    Attributes:
        message: Human-readable error message.
        code: Stable internal error code identifying the error type.
        http_status: HTTP status code associated with the error.
    """

    def __init__(
        self,
        message: str = "ClickUp write operation failed.",
        http_status: int = 502,
    ):
        """
        Initialize a ClickUp write exception.

        Args:
            message (str): Human-readable error message.
            http_status (int): HTTP status code returned for the error (default: 502).
        """
        super().__init__(
            message=message,
            code="CLICKUP_WRITE_ERROR",
            http_status=http_status,
        )