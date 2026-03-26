"""Invalid member data exception."""

from backend.src.domain.exceptions.app_exception import AppException


class InvalidMemberDataException(AppException):
    """Raised when member payload misses required fields."""
    def __init__(self, missing_fields: list[str], data: dict = None):
        """Initialize an invalid member data exception.

        Args:
            missing_fields: Required fields that are missing.
            data: Optional payload to include in the message.
        """
        fields = ", ".join(missing_fields)
        detail = f" — received: {data}" if data else ""
        super().__init__(
            message=f"Invalid member data, missing required fields: {fields}{detail}",
            code="INVALID_MEMBER_DATA",
            http_status=400
        )