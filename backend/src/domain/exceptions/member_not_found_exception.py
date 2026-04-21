"""
Member not found exception.

This module defines the MemberNotFoundException, raised when a requested member
cannot be found using the provided identifier (such as ID or email).
"""

from backend.src.domain.exceptions.app_exception import AppException


class MemberNotFoundException(AppException):
    """
    Exception raised when a member cannot be found.

    This exception is used when a member lookup operation fails because the requested
    member does not exist in the system or cannot be retrieved using the given identifier.

    Attributes:
        message (str): Human-readable error message describing the missing member.
        code (str): Internal error code identifying the member not found error.
        http_status (int): HTTP status code returned to the client.
    """

    def __init__(self, message: str = "Member not found with ID/email."):
        """
        Initialize a MemberNotFoundException.

        Args:
            message (str): Error message describing the missing member
                (default: "Member not found with ID/email.").
        """
        super().__init__(
            message=message,
            code="MEMBER_NOT_FOUND",
            http_status=404,
        )