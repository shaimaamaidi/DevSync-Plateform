"""
Missing environment variable exception.

This module defines the MissingEnvVariableException, raised when a required environment variable is missing.
"""

from backend.src.domain.exceptions.app_exception import AppException


class MissingEnvVariableException(AppException):
    """
    Exception raised when a required environment variable is missing.

    Args:
        var_name: Name of the missing environment variable.
    """
    def __init__(self, var_name: str):
        message = f"Missing required environment variable: {var_name}"
        super().__init__(message=message, code="MISSING_ENV", http_status=500)