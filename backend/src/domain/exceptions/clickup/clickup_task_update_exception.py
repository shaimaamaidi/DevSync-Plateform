"""
ClickUp task update exception.

This module defines the ClickUpTaskUpdateException, a specialized exception used
to handle failures that occur when updating tasks in ClickUp. It standardizes
error reporting for task update operations.
"""

from backend.src.domain.exceptions.base.app_exception import AppException


class ClickUpTaskUpdateException(AppException):
    """
    Exception for ClickUp task update failures.

    This exception is raised when an error occurs while attempting to update
    a task in ClickUp. It provides a consistent structure for representing
    task update failures within the application.

    Attributes:
        message: Human-readable error message.
        code: Stable internal error code identifying the error type.
        http_status: HTTP status code associated with the error.
    """

    def __init__(self, message: str = "Failed to update task.", http_status: int = 502):
        """
        Initialize a ClickUp task update exception.

        Args:
            message (str): Human-readable error message.
            http_status (int): HTTP status code returned for the error (default: 502).
        """
        super().__init__(
            message=message,
            code="CLICKUP_TASK_UPDATE_ERROR",
            http_status=http_status
        )