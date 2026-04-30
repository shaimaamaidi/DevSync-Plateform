"""
ClickUp empty space exception.

This module defines the ClickUpEmptySpaceException, a specialized exception used
to handle cases where a valid ClickUp space contains no folders. It standardizes
error reporting for empty resource scenarios returned by the ClickUp API.
"""

from backend.src.domain.exceptions.base.app_exception import AppException


class ClickUpEmptySpaceException(AppException):
    """
    Exception for empty ClickUp space errors.

    This exception is raised when a valid ClickUp space is found but contains
    no folders. It provides a consistent structure for representing empty
    resource scenarios within the application.

    Attributes:
        message: Human-readable error message.
        code: Stable internal error code identifying the error type.
        http_status: HTTP status code associated with the error.
    """

    def __init__(self, message: str = "No folder found in the ClickUp space.", http_status: int = 404):
        """
        Initialize a ClickUp empty space exception.

        Args:
            message (str): Human-readable error message.
            http_status (int): HTTP status code returned for the error (default: 404).
        """
        super().__init__(
            message=message,
            code="CLICKUP_EMPTY_SPACE",
            http_status=http_status
        )