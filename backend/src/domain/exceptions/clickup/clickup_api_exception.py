"""
ClickUp API exception.

This module defines the ClickUpApiException, a specialized exception used to handle
errors returned by the ClickUp API. It standardizes error reporting for external API
failures, including HTTP errors (4xx / 5xx).
"""

from backend.src.domain.exceptions.base.app_exception import AppException


class ClickUpApiException(AppException):
    """
    Exception for ClickUp API errors.

    This exception is raised when an unexpected error occurs while communicating
    with the ClickUp API. It provides a consistent structure for representing
    external service failures within the application.

    Attributes:
        message: Human-readable error message.
        code: Stable internal error code identifying the error type.
        http_status: HTTP status code associated with the error.
    """

    def __init__(self, message: str = "Unexpected ClickUp API error.", http_status: int = 424):
        """
        Initialize a ClickUp API exception.

        Args:
            message (str): Human-readable error message.
            http_status (int): HTTP status code returned for the error (default: 502).
        """
        super().__init__(
            message=message,
            code="CLICKUP_API_ERROR",
            http_status=http_status
        )