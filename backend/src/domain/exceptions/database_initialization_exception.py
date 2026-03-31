"""
Database initialization exception.

This module defines the DatabaseInitializationException, raised when database initialization fails.
"""

from backend.src.domain.exceptions.app_exception import AppException


class DatabaseInitializationException(AppException):
    """
    Exception raised when database initialization fails.

    Attributes:
        message (str): Error message override.
        code (str): Error code.
        http_status (int): HTTP status to return.
    """
    def __init__(self, message: str = "Failed to initialize or create the database."):
        """
        Initialize a database initialization exception.

        Args:
            message (str): Error message (default: "Failed to initialize or create the database.").
        """
        super().__init__(
            message=message,
            code="DB_INIT_ERROR",
            http_status=500
        )