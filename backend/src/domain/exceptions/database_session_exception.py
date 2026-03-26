"""Database session exception."""

from backend.src.domain.exceptions.app_exception import AppException


class DatabaseSessionException(AppException):
    """Raised when database session creation fails."""
    def __init__(self):
        """Initialize a database session exception."""
        super().__init__(
            message="Failed to create or retrieve database session",
            code="DB_SESSION_ERROR",
            http_status=500
        )