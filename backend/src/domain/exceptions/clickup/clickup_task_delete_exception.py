"""
ClickUp task delete exception.

This module defines the ClickUpTaskDeleteException, a specialized exception used
to handle failures that occur when deleting tasks in ClickUp. It standardizes
error reporting for task deletion operations.
"""

from backend.src.domain.exceptions.clickup.clickup_write_exception import ClickUpWriteException


class ClickUpTaskDeleteException(ClickUpWriteException):
    """
    Exception for ClickUp task deletion failures.

    This exception is raised when an error occurs while attempting to delete
    a task in ClickUp. It provides a consistent structure for representing
    task deletion failures within the application.

    Attributes:
        message: Human-readable error message.
        code: Stable internal error code identifying the error type.
        http_status: HTTP status code associated with the error.
    """

    def __init__(self, message: str = "Failed to delete task.", http_status: int = 502):
        """
        Initialize a ClickUp task deletion exception.

        Args:
            message (str): Human-readable error message.
            http_status (int): HTTP status code returned for the error (default: 502).
        """
        super().__init__(
            message=message,
            http_status=http_status
        )
        self.code = "CLICKUP_TASK_DELETE_ERROR"