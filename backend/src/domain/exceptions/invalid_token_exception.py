"""
Invalid token exception.

This module defines the InvalidTokenException, raised when a JWT token is invalid or expired.
"""

from backend.src.domain.exceptions.app_exception import AppException


class InvalidTokenException(AppException):
    """
    Exception raised for an invalid or expired JWT token.

    Attributes:
        message (str): Error message override.
        code (str): Error code.
        http_status (int): HTTP status to return.
    """
    def __init__(self, message: str = "Invalid or expired token."):
        """
        Initialize an invalid token exception.

        Args:
            message (str): Error message (default: "Invalid or expired token.").
        """
        super().__init__(message=message, code="INVALID_TOKEN", http_status=401)