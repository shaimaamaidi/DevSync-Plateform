"""
Refresh token persistence exception.

This module defines the RefreshTokenPersistenceException, raised when a refresh token persistence operation fails.
"""

from backend.src.domain.exceptions.app_exception import AppException


class RefreshTokenPersistenceException(AppException):
    """
    Exception raised when a refresh token persistence operation fails.
    Attributes:
        message (str): Error message override.
        code (str): Error code.
        http_status (int): HTTP status to return.
    """
    def __init__(self, message: str = "A refresh token persistence error occurred."):
        """
        Initialize a refresh token persistence exception.

        Args:
            message (str): Error message (default: "A refresh token persistence error occurred.").
        """
        super().__init__(
            message=message,
            code="REFRESH_TOKEN_PERSISTENCE_ERROR",
            http_status=500,
        )