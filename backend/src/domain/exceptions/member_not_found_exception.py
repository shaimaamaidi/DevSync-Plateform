"""
Member not found exception.

This module defines the MemberNotFoundException, raised when a member cannot be found.
"""

from backend.src.domain.exceptions.app_exception import AppException


class MemberNotFoundException(AppException):
    """
    Exception raised when a member cannot be found.

    Attributes:
        message (str): Error message override.
        code (str): Error code.
        http_status (int): HTTP status to return.
    """
    def __init__(self, message="Member not found with ID/email."):
        """
        Initialize a member not found exception.

        Args:
            message (str): Error message (default: "Member not found with ID/email.").
        """
        super().__init__(
            message=message,
            code="MEMBER_NOT_FOUND",
            http_status=404
        )
