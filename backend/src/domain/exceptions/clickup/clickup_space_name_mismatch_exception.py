"""
ClickUp space name mismatch exception module.

This module defines the ClickUpSpaceNameMismatchException, which is raised
when a ClickUp space is found but its actual name does not match the expected
name. It is used to detect inconsistencies or conflicts during workspace
validation or synchronization with ClickUp.
"""

from backend.src.domain.exceptions.base.app_exception import AppException


class ClickUpSpaceNameMismatchException(AppException):
    """
    Exception raised when a ClickUp space name does not match the expected value.

    This exception is used when a space is found with a given identifier,
    but its actual name differs from the expected one, indicating a potential
    inconsistency in ClickUp data.

    Attributes:
        expected: The expected space name.
        actual: The actual space name retrieved from ClickUp.
    """

    def __init__(self, expected: str, actual: str):
        """
        Initialize the ClickUpSpaceNameMismatchException.

        Args:
            expected (str): The expected space name.
            actual (str): The actual space name retrieved.
        """
        super().__init__(
            message=f"Space name mismatch: expected '{expected}', got '{actual}'.",
            code="CLICKUP_SPACE_NAME_MISMATCH",
            http_status=409,
        )