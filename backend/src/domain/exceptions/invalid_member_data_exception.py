"""
Invalid member data exception.

This module defines the InvalidMemberDataException, raised when a member payload is invalid
or missing required fields during validation or processing.
"""

from backend.src.domain.exceptions.app_exception import AppException


class InvalidMemberDataException(AppException):
    """
    Exception raised when member data validation fails.

    This exception is used when a member payload is missing required fields or contains
    invalid data, preventing correct processing or persistence.

    Attributes:
        message (str): Human-readable error message describing the validation failure.
        code (str): Internal error code identifying the member data validation error.
        http_status (int): HTTP status code returned to the client.
    """

    def __init__(self, missing_fields: list[str], data: dict = None):
        """
        Initialize an InvalidMemberDataException.

        Args:
            missing_fields (list[str]): List of required fields that are missing.
            data (dict, optional): Optional payload to include for debugging context.
        """
        fields = ", ".join(missing_fields)
        detail = f" — received: {data}" if data else ""

        super().__init__(
            message=f"Invalid member data, missing required fields: {fields}{detail}",
            code="INVALID_MEMBER_DATA",
            http_status=400,
        )