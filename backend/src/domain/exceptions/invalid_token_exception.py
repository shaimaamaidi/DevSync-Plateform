"""
Invalid token exception.

This module defines the InvalidTokenException, raised when a JWT token is invalid,
expired, or cannot be authenticated.
"""

from backend.src.domain.exceptions.app_exception import AppException


class InvalidTokenException(AppException):
    """
    Exception raised when a JWT token is invalid or expired.

    This exception is used during authentication when the provided token cannot be
    verified, has expired, or is malformed, preventing access to protected resources.

    Attributes:
        message (str): Human-readable error message describing the authentication failure.
        code (str): Internal error code identifying the token validation error.
        http_status (int): HTTP status code returned to the client.
    """

    def __init__(self, message: str = "Invalid or expired token."):
        """
        Initialize an InvalidTokenException.

        Args:
            message (str): Error message describing the token issue
                (default: "Invalid or expired token.").
        """
        super().__init__(
            message=message,
            code="INVALID_TOKEN",
            http_status=401,
        )