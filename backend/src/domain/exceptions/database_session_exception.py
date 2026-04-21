"""
Database session exception.

This module defines the DatabaseSessionException, raised when the creation or retrieval
of a database session fails.
"""

from backend.src.domain.exceptions.app_exception import AppException


class DatabaseSessionException(AppException):
    """
    Exception raised when database session creation or retrieval fails.

    This exception is used to indicate that the application cannot obtain a valid database session,
    often due to connection issues, misconfiguration, or internal database errors.

    Attributes:
        message (str): Human-readable error message describing the session failure.
        code (str): Internal error code identifying the database session error.
        http_status (int): HTTP status code returned to the client.
    """

    def __init__(self):
        """
        Initialize a DatabaseSessionException.

        This exception uses a default message indicating that the database session could not be created
        or retrieved successfully.
        """
        super().__init__(
            message="Failed to create or retrieve database session.",
            code="DB_SESSION_ERROR",
            http_status=500,
        )