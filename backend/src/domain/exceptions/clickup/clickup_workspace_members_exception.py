"""
ClickUp workspace members exception.

This module defines the ClickUpWorkspaceMembersException, a specialized exception used
to handle failures when retrieving members from a ClickUp workspace. It standardizes
error reporting for workspace member access issues.
"""

from backend.src.domain.exceptions.base.app_exception import AppException


class ClickUpWorkspaceMembersException(AppException):
    """
    Exception for ClickUp workspace member retrieval failures.

    This exception is raised when workspace members cannot be retrieved from
    ClickUp, either due to a missing workspace, API failure, or empty response.
    It provides a consistent structure for representing member-related errors.

    Attributes:
        message: Human-readable error message.
        code: Stable internal error code identifying the error type.
        http_status: HTTP status code associated with the error.
    """

    def __init__(self, message: str = "Unable to retrieve workspace members.", http_status: int = 404):
        """
        Initialize a ClickUp workspace members exception.

        Args:
            message (str): Human-readable error message.
            http_status (int): HTTP status code returned for the error (default: 404).
        """
        super().__init__(
            message=message,
            code="CLICKUP_MEMBERS_ERROR",
            http_status=http_status
        )