"""
Database connection exception.

This module defines the DatabaseConnectionException, raised when database connection fails.
"""

from backend.src.domain.exceptions.app_exception import AppException


class DatabaseConnectionException(AppException):
    """
    Exception raised when database connection fails.
    """
    def __init__(self):
        """Initialize a database connection exception."""
        super().__init__(
            message="Failed to connect to the database",
            code="DB_CONNECTION_ERROR",
            http_status=500
        )