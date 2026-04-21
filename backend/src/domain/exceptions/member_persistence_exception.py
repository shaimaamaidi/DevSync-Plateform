"""
Member persistence exception.

This module defines the MemberPersistenceException, raised when an error occurs during
member persistence operations such as database access, retrieval, or storage failures.
"""

from backend.src.domain.exceptions.app_exception import AppException


class MemberPersistenceException(AppException):
    """
    Exception raised when member persistence operations fail.

    This exception is used to indicate failures occurring while accessing or manipulating
    member data in the persistence layer (e.g., database errors, repository failures).

    Attributes:
        message (str): Human-readable error message describing the persistence failure.
        code (str): Internal error code identifying the member persistence error.
        http_status (int): HTTP status code returned to the client.
    """

    def __init__(self, message: str = "Error occurred while accessing member data."):
        """
        Initialize a MemberPersistenceException.

        Args:
            message (str): Error message describing the persistence failure
                (default: "Error occurred while accessing member data").
        """
        super().__init__(
            message=message,
            code="MEMBER_PERSISTENCE_ERROR",
            http_status=500,
        )