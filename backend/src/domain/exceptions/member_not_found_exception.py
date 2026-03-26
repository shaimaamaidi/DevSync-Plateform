"""Member not found exception."""

from backend.src.domain.exceptions.app_exception import AppException


class MemberNotFoundException(AppException):
    """Raised when a member cannot be found."""
    def __init__(self, message=f"Member not found with ID/email"):
        """Initialize a member not found exception.

        Args:
            message: Error message override.
        """
        super().__init__(
            message=message,
            code="MEMBER_NOT_FOUND",
            http_status=404
        )
