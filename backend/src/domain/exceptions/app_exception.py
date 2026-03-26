
"""Base application exception with metadata."""


class AppException(Exception):
    """Exception carrying a code and HTTP status."""
    def __init__(self, message: str, code: str = "APP_ERROR", http_status: int = 400):
        """Initialize an application exception.

        Args:
            message: Human readable error message.
            code: Stable error code.
            http_status: HTTP status to return.
        """
        self.message = message
        self.code = code
        self.http_status = http_status
        super().__init__(message)