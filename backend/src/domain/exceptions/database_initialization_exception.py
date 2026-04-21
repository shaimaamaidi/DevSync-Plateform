"""
Database initialization exception.

This module defines the DatabaseInitializationException, raised when the database
fails to initialize or cannot be created properly during application startup.
"""

from backend.src.domain.exceptions.app_exception import AppException


class DatabaseInitializationException(AppException):
    """
    Exception raised when database initialization fails.

    This exception is used to indicate failures occurring during database setup or initialization,
    such as schema creation issues, migration failures, or misconfiguration.

    Attributes:
        message (str): Human-readable error message describing the initialization failure.
        code (str): Internal error code identifying the database initialization error.
        http_status (int): HTTP status code returned to the client.
    """

    def __init__(self, message: str = "Failed to initialize or create the database."):
        """
        Initialize a DatabaseInitializationException.

        Args:
            message (str): Error message describing the initialization failure
                (default: "Failed to initialize or create the database.").
        """
        super().__init__(
            message=message,
            code="DB_INIT_ERROR",
            http_status=500,
        )