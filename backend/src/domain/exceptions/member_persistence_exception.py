"""
Member persistence exception.

This module defines the MemberPersistenceException, raised when member persistence operations fail.
"""

from backend.src.domain.exceptions.app_exception import AppException


class MemberPersistenceException(AppException):
    """
    Exception raised when member persistence fails.

    Args:
        msg: Error message override.
    """
    def __init__(self, msg: str = "Error occurred while accessing member data"):
        """Initialize a member persistence exception.

        Args:
            msg: Error message override.
        """
        super().__init__(
            message=msg,
            code="MEMBER_PERSISTENCE_ERROR",
            http_status=500
        )