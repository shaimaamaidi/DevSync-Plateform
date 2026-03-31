"""
Invalid input exception.

This module defines the InvalidInputException, raised when input validation fails.
"""

from backend.src.domain.exceptions.app_exception import AppException


class InvalidInputException(AppException):
    """
    Exception raised when input validation fails.

    Attributes:
        message (str): Error message override.
        code (str): Error code.
        http_status (int): HTTP status to return.
    """
    def __init__(self, message: str = "Invalid input.", details: dict = None):
        """
        Initialize an invalid input exception.

        Args:
            message (str): Error message (default: "Invalid input.").
            details (dict): Extra validation details.
        """
        super().__init__(message=message, code="INVALID_INPUT", http_status=422)
        self.details = details or {}        
