"""Base application exception for domain-specific errors."""

class AppException(Exception):
    """Base exception for domain and business logic errors.

    Attributes:
        message: Human-readable error message.
        code: Error code identifier.
        http_status: HTTP status code for API responses.
    """

    def __init__(self, message: str, code: str = "APP_ERROR", http_status: int = 400):
        """Initialize the exception.

        Args:
            message: Human-readable error message.
            code: Error code identifier.
            http_status: HTTP status code to return.
        """
        self.message = message
        self.code = code
        self.http_status = http_status
        super().__init__(message)