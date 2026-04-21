"""
Base application exception.

This module defines the AppException, a base exception used across the application
to standardize error handling by carrying a message, an error code, and an HTTP status.
"""

class AppException(Exception):
    """
    Base exception for application-level errors.

    This exception is the parent class for all custom application exceptions.
    It provides a standardized structure for error reporting, including a message,
    a stable error code, and an HTTP status code for API responses.

    Attributes:
        message: Human-readable error message.
        code: Stable internal error code identifying the type of error.
        http_status: HTTP status code associated with the error.
    """

    def __init__(self, message: str, code: str = "APP_ERROR", http_status: int = 400):
        """
        Initialize a base application exception.

        Args:
            message (str): Human-readable error message.
            code (str): Stable error code (default: "APP_ERROR").
            http_status (int): HTTP status code to return (default: 400).
        """
        self.message = message
        self.code = code
        self.http_status = http_status
        super().__init__(message)