"""
ClickUp space not found exception.

This module defines the ClickUpSpaceNotFoundException, raised when a ClickUp space does not exist.
"""

from backend.src.domain.exceptions.app_exception import AppException


class ClickUpSpaceNotFoundException(AppException):
    """
    Exception raised when a ClickUp space does not exist.

    Attributes:
        message (str): Error message override.
        code (str): Error code.
        http_status (int): HTTP status to return.
    """
    def __init__(self, message="ClickUp space not found with ID/SPACE_CODE."):
        """
        Initialize a ClickUp space not found exception.

        Args:
            message (str): Error message (default: "ClickUp space not found with ID/SPACE_CODE.").
        """
        super().__init__(
            message=message,
            code="CLICKUP_SPACE_NOT_FOUND",
            http_status=404
        )