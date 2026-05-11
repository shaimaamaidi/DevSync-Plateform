"""
ClickUp space not found exception.

This module defines the ClickUpSpaceNotFoundException, raised when a ClickUp space does not exist
or cannot be found using the provided identifier.
"""

from backend.src.domain.exceptions.base.app_exception import AppException


class ClickUpSpaceNotFoundException(AppException):
    """
    Exception raised when a ClickUp space is not found in database.

    This exception is used when a requested ClickUp space cannot be located using its ID or space code.
    It typically indicates that the resource does not exist in ClickUp or is inaccessible.

    Attributes:
        message (str): Human-readable error message describing the missing ClickUp space.
        code (str): Internal error code identifying the type of error.
        http_status (int): HTTP status code returned to the client.
    """

    def __init__(self, message: str = "ClickUp space not found with ID/SPACE_CODE."):
        """
        Initialize a ClickUpSpaceNotFoundException.

        Args:
            message (str): Error message describing the missing ClickUp space
                (default: "ClickUp space not found with ID/SPACE_CODE.").
        """
        super().__init__(
            message=message,
            code="CLICKUP_SPACE_NOT_FOUND",
            http_status=404,
        )