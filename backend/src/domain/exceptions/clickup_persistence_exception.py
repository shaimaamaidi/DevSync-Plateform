"""
ClickUp persistence error exception.

This module defines the ClickUpPersistenceException, raised when ClickUp storage operations fail.
"""

from backend.src.domain.exceptions.app_exception import AppException


class ClickUpPersistenceException(AppException):
    """
    Exception raised when ClickUp storage operations fail.

    Attributes:
        message (str): Error message override.
        code (str): Error code.
        http_status (int): HTTP status to return.
    """
    def __init__(self, message: str = "Error occurred while accessing ClickUp space data."):
        """
        Initialize a ClickUp persistence exception.

        Args:
            message (str): Error message (default: "Error occurred while accessing ClickUp space data.").
        """
        super().__init__(
            message=message,
            code="CLICKUP_PERSISTENCE_ERROR",
            http_status=500
        )