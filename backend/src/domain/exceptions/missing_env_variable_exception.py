"""
Missing environment variable exception.

This module defines the MissingEnvVariableException, raised when a required environment variable
is not found in the application configuration.
"""

from backend.src.domain.exceptions.app_exception import AppException


class MissingEnvVariableException(AppException):
    """
    Exception raised when a required environment variable is missing.

    This exception is used to indicate that a mandatory configuration value is not present
    in the environment, preventing the application from properly initializing or running.

    Attributes:
        message (str): Human-readable error message describing the missing variable.
        code (str): Internal error code identifying the type of configuration error.
        http_status (int): HTTP status code returned to the client.
    """

    def __init__(self, message: str = "Missing required environment variable."):
        """
        Initialize a MissingEnvVariableException.

        Args:
            message (str): Message describing the missing environment variable.
        """
        super().__init__(
            message=message,
            code="MISSING_ENV_VARIABLE",
            http_status=500
        )