"""
ClickUp resource not found exception.

This module defines the ClickUpResourceNotFoundException, a specialized exception
used to handle cases where a requested resource does not exist in ClickUp.
It standardizes error reporting for missing resource scenarios.
"""

from backend.src.domain.exceptions.base.app_exception import AppException


class ClickUpResourceNotFoundException(AppException):
    """
    Exception for missing ClickUp resources.

    This exception is raised when a requested resource (such as a space, folder,
    list, or task) cannot be found in ClickUp. It provides a consistent structure
    for representing not-found errors within the application.

    Attributes:
        message: Human-readable error message.
        code: Stable internal error code identifying the error type.
        http_status: HTTP status code associated with the error.
    """

    def __init__(self, message: str = "ClickUp resource not found.", http_status: int = 404):
        """
        Initialize a ClickUp resource not found exception.

        Args:
            message (str): Human-readable error message.
            http_status (int): HTTP status code returned for the error (default: 404).
        """
        super().__init__(
            message=message,
            code="CLICKUP_RESOURCE_NOT_FOUND",
            http_status=http_status
        )