"""
ClickUp client error exception.

This module defines the ClickUpClientException, a specialized exception used
to handle client-side errors (HTTP 4xx) returned by the ClickUp API.
It standardizes error reporting for invalid request scenarios.
"""

from backend.src.domain.exceptions.base.app_exception import AppException


class ClickUpClientException(AppException):
    """
    Exception for ClickUp client-side errors.

    This exception is raised when a request to the ClickUp API fails due to
    client-side issues (e.g., bad request, unauthorized, forbidden, not found).
    These errors indicate invalid input or configuration and should NOT be retried.

    Attributes:
        message: Human-readable error message.
        code: Stable internal error code identifying the error type.
        http_status: HTTP status code associated with the error.
    """

    def __init__(self, message: str, http_status: int = 500):
        """
        Initialize a ClickUp client exception.

        Args:
            message (str): Human-readable error message.
            http_status (int): HTTP status code returned by ClickUp API (default: 400).
        """
        super().__init__(
            message=message,
            code="CLICKUP_CLIENT_ERROR",
            http_status=http_status
        )