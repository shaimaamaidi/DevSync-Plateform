"""
Refresh token persistence exception.

This module defines the RefreshTokenPersistenceException, raised when an error occurs during
refresh token persistence operations such as saving, retrieving, or updating refresh tokens.
"""

from backend.src.domain.exceptions.base.app_exception import AppException


class RefreshTokenPersistenceException(AppException):
    """
    Exception raised when a refresh token persistence operation fails.

    This exception is used to indicate failures occurring in the persistence layer while handling
    refresh tokens, such as database errors or repository access issues.

    Attributes:
        message (str): Human-readable error message describing the persistence failure.
        code (str): Internal error code identifying the refresh token persistence error.
        http_status (int): HTTP status code returned to the client.
    """

    def __init__(self, message: str = "A refresh token persistence error occurred."):
        """
        Initialize a RefreshTokenPersistenceException.

        Args:
            message (str): Error message describing the persistence failure
                (default: "A refresh token persistence error occurred.").
        """
        super().__init__(
            message=message,
            code="REFRESH_TOKEN_PERSISTENCE_ERROR",
            http_status=500,
        )