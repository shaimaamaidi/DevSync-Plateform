"""
ClickUp task creation exception.

This module defines the ClickUpTaskCreateException, a specialized exception used
to handle failures that occur when creating tasks in ClickUp. It standardizes
error reporting for task creation operations.
"""

from backend.src.domain.exceptions.base.app_exception import AppException


class ClickUpTaskCreateException(AppException):
    """
    Exception for ClickUp task creation failures.

    This exception is raised when an error occurs while attempting to create
    a task in ClickUp. It provides a consistent structure for representing
    task creation failures within the application.

    Attributes:
        message: Human-readable error message.
        code: Stable internal error code identifying the error type.
        http_status: HTTP status code associated with the error.
    """

    def __init__(self, message: str = "Failed to create task.", http_status: int = 502):
        """
        Initialize a ClickUp task creation exception.

        Args:
            message (str): Human-readable error message.
            http_status (int): HTTP status code returned for the error (default: 502).
        """
        super().__init__(
            message=message,
            code="CLICKUP_TASK_CREATE_ERROR",
            http_status=http_status
        )