"""
Tool parsing exception.

This module defines the ToolParsingException, raised when tool input arguments
cannot be parsed correctly (e.g., invalid JSON or malformed payload).

It is used in tool-calling pipelines to separate parsing/format errors from
validation and execution errors.
"""

from backend.src.domain.exceptions.base.app_exception import AppException


class ToolParsingException(AppException):
    """
    Exception raised when tool arguments cannot be parsed.

    This exception is used when:
    - Tool input JSON is malformed or invalid
    - Required parsing of arguments fails before validation
    - The payload cannot be deserialized into expected structures

    Attributes:
        message (str): Human-readable description of the parsing error.
        code (str): Internal error code identifying the parsing failure type.
        http_status (int): HTTP status code returned to the client.
    """

    def __init__(self, message: str = "Failed to parse tool arguments."):
        """
        Initialize a ToolParsingException.

        Args:
            message (str): Description of why tool parsing failed.
        """
        super().__init__(
            message=message,
            code="TOOL_PARSING_ERROR",
            http_status=400
        )