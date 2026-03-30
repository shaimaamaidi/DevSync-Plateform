"""
ClickUp persistence error exception.

This module defines the ClickUpPersistenceException, raised when ClickUp storage operations fail.
"""

from backend.src.domain.exceptions.app_exception import AppException


class ClickUpPersistenceException(AppException):
    """
    Exception raised when ClickUp storage operations fail.

    Args:
        msg: Error message override.
    """
    def __init__(self, msg: str = "Error occurred while accessing ClickUp space data"):
        """Initialize a ClickUp persistence exception.

        Args:
            msg: Error message override.
        """
        super().__init__(
            message=msg,
            code="CLICKUP_PERSISTENCE_ERROR",
            http_status=500
        )