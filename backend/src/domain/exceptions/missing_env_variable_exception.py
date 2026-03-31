"""
Missing environment variable exception.

This module defines the MissingEnvVariableException, raised when a required environment variable is missing.
"""

from backend.src.domain.exceptions.app_exception import AppException


class MissingEnvVariableException(AppException):
    """
    Exception raised when a required environment variable is missing.

    Attributes:
        message (str): Error message override.
        code (str): Error code.
        http_status (int): HTTP status to return.
    """
    def __init__(self, var_name: str):
        """
        Initialize a missing env's variables exception.

        Args:
            var_name (str): Name of the missing environment variable.
        """
        message = f"Missing required environment variable: {var_name}"
        super().__init__(message=message, code="MISSING_ENV", http_status=500)