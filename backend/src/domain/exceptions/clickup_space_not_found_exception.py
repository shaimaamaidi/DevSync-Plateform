"""ClickUp space not found exception."""

from backend.src.domain.exceptions.app_exception import AppException


class ClickUpSpaceNotFoundException(AppException):
    """Raised when a ClickUp space does not exist."""
    def __init__(self, message="ClickUp space not found with ID/SPACE_CODE"):
        """Initialize a ClickUp space not found exception.

        Args:
            message: Error message override.
        """
        super().__init__(
            message=message,
            code="CLICKUP_SPACE_NOT_FOUND",
            http_status=404
        )