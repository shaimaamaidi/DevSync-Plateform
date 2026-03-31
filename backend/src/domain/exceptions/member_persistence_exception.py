"""
Member persistence exception.

This module defines the MemberPersistenceException, raised when member persistence operations fail.
"""

from backend.src.domain.exceptions.app_exception import AppException


class MemberPersistenceException(AppException):
    """
    Exception raised when member persistence fails.

    Attributes:
        message (str): Error message override.
        code (str): Error code.
        http_status (int): HTTP status to return.
    """
    def __init__(self, message: str = "Error occurred while accessing member data"):
        """
        Initialize a member persistence exception.

        Args:
            message (str): Error message (default: "Error occurred while accessing member data".).
        """
        super().__init__(
            message=message,
            code="MEMBER_PERSISTENCE_ERROR",
            http_status=500
        )