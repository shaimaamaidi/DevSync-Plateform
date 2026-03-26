"""ClickUp persistence error exception."""

from backend.src.domain.exceptions.app_exception import AppException


class ClickUpPersistenceException(AppException):
    """Raised when ClickUp storage operations fail."""
    def __init__(self, msg: str = "Error occurred while accessing ClickUp space data"):
        """Initialize a ClickUp persistence exception.

        Args:
            msg: Error message override.
        """
        super().__init__(
            message=msg,
            code="CLICKUP_PERSISTENCE_ERROR",
            http_status=500
        )