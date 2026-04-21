"""
Invalid tool argument exception module.

This module defines the InvalidToolArgumentException, raised when a tool
is invoked with invalid, missing, or malformed input arguments that do not
match the expected schema or domain contract.
"""

from backend.src.domain.exceptions.app_exception import AppException


class InvalidToolArgumentException(AppException):
    """
    Exception raised when a tool is called with invalid or malformed arguments.

    This exception is used to indicate validation-level failures in tool-calling
    pipelines, including:
    - Malformed JSON input
    - Missing required parameters
    - Schema mismatch with tool contract
    - Failed domain object deserialization

    It distinguishes input validation errors from runtime or infrastructure failures.

    Attributes:
        message (str): Human-readable error message describing the validation failure.
        code (str): Internal error code identifying invalid tool argument errors.
        http_status (int): HTTP status code returned to the client.
    """

    def __init__(self, message: str = "Invalid tool arguments."):
        """
        Initialize an invalid tool argument exception.

        Args:
            message (str): Error message describing the validation issue.
        """
        super().__init__(
            message=message,
            code="INVALID_TOOL_ARGUMENT",
            http_status=422,
        )