"""
Backlog generation exception.

This module defines the BacklogGenerationException, raised when the backlog generation pipeline fails.
"""

from backend.src.domain.exceptions.base.app_exception import AppException


class BacklogGenerationException(AppException):
    """
    Exception raised when the backlog generation pipeline fails.

    Attributes:
        message (str): Human-readable error message.
        code (str): Error code.
        http_status (int): HTTP status to return.
    """

    def __init__(self, message: str = "Backlog generation failed."):
        """
        Initialize a backlog generation exception.

        Args:
            message (str): Human-readable error message.
        """
        super().__init__(
            message=message,
            code="BACKLOG_GENERATION_ERROR",
            http_status=500
        )