"""
Base application exception.

This module defines the AppException, a base exception carrying a code and HTTP status for application errors.
"""


class AppException(Exception):
    """
    Base exception carrying a code and HTTP status for application errors.

    Attributes:
        message (str): Human readable error message.
        code (str): Stable error code.
        http_status (int): HTTP status to return.
    """
    def __init__(self, message: str, code: str = "APP_ERROR", http_status: int = 400):
        """
        Initialize an application exception.

        Args:
            message (str): Human readable error message.
            code (str): Stable error code.
            http_status (int): HTTP status to return.
        """
        self.message = message
        self.code = code
        self.http_status = http_status
        super().__init__(message)