"""
Database connection exception.

This module defines the DatabaseConnectionException, raised when a database connection
cannot be established or fails during runtime.
"""

from backend.src.domain.exceptions.app_exception import AppException


class DatabaseConnectionException(AppException):
    """
    Exception raised when a database connection fails.

    This exception is used to indicate that the application is unable to connect
    to the database due to configuration issues, network problems, or service unavailability.

    Attributes:
        message (str): Human-readable error message describing the connection failure.
        code (str): Internal error code identifying the database connection error.
        http_status (int): HTTP status code returned to the client.
    """

    def __init__(self):
        """
        Initialize a DatabaseConnectionException.

        This exception uses a default message indicating that the database connection failed.
        """
        super().__init__(
            message="Failed to connect to the database",
            code="DB_CONNECTION_ERROR",
            http_status=500,
        )