"""
Database initialization exception.

This module defines the DatabaseInitializationException, raised when database initialization fails.
"""

from backend.src.domain.exceptions.app_exception import AppException


class DatabaseInitializationException(AppException):
    """
    Exception raised when database initialization fails.

    Args:
        msg: Error message override.
    """
    def __init__(self, msg: str = "Failed to initialize or create the database"):
        """Initialize a database initialization exception.

        Args:
            msg: Error message override.
        """
        super().__init__(
            message=msg,
            code="DB_INIT_ERROR",
            http_status=500
        )