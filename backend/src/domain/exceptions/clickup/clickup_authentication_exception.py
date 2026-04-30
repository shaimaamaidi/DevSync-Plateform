"""
ClickUp authentication exception.

This module defines the ClickUpAuthenticationException, a specialized exception used
to handle authentication failures when interacting with the ClickUp API. It standardizes
error reporting for cases involving missing or invalid credentials.
"""

from backend.src.domain.exceptions.base.app_exception import AppException


class ClickUpAuthenticationException(AppException):
    """
    Exception for ClickUp authentication errors.

    This exception is raised when authentication with the ClickUp API fails,
    such as when an API token is missing, invalid, or expired. It provides a
    consistent structure for representing authentication-related failures.

    Attributes:
        message: Human-readable error message.
        code: Stable internal error code identifying the error type.
        http_status: HTTP status code associated with the error.
    """

    def __init__(self, message: str = "Missing or invalid ClickUp token.", http_status: int = 401):
        """
        Initialize a ClickUp authentication exception.

        Args:
            message (str): Human-readable error message.
            http_status (int): HTTP status code returned for the error (default: 401).
        """
        super().__init__(
            message=message,
            code="CLICKUP_AUTH_ERROR",
            http_status=http_status
        )