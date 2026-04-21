"""
Tool execution exception.

This module defines the ToolExecutionException, raised when a domain tool
fails during execution.

It is used in tool-calling pipelines to indicate unexpected runtime errors
occurring inside domain tools after input validation has passed.
"""

from backend.src.domain.exceptions.app_exception import AppException


class ToolExecutionException(AppException):
    """
    Exception raised when a tool execution fails.

    This exception is used when:
    - A domain tool raises an unexpected runtime error
    - External services used by the tool fail during execution
    - The tool orchestration logic encounters an internal failure

    Attributes:
        message (str): Human-readable description of the error.
        code (str): Internal error code identifying the tool failure type.
        http_status (int): HTTP status code returned to the client.
    """

    def __init__(self, message: str = "Tool execution failed."):
        """
        Initialize a ToolExecutionException.

        Args:
            message (str): Description of the tool execution failure.
        """
        super().__init__(
            message=message,
            code="TOOL_EXECUTION_ERROR",
            http_status=500
        )