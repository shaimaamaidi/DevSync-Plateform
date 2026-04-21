"""
Invalid input exception.

This module defines the InvalidInputException, raised when input validation fails
due to missing, incorrect, or malformed data provided by the user or external systems.
"""

from backend.src.domain.exceptions.base.app_exception import AppException


class InvalidInputException(AppException):
    """
    Exception raised when input validation fails.

    This exception is used when provided input does not satisfy validation rules,
    such as incorrect format, missing required fields, or invalid values.
    It may also carry additional details describing validation errors.

    Attributes:
        message (str): Human-readable error message describing the validation failure.
        code (str): Internal error code identifying the validation error.
        http_status (int): HTTP status code returned to the client.
    """

    def __init__(self, message: str = "Invalid input."):
        """
        Initialize an InvalidInputException.

        Args:
            message (str): Error message describing the validation failure (default: "Invalid input.").
        """
        super().__init__(
            message=message,
            code="INVALID_INPUT",
            http_status=422,
        )
