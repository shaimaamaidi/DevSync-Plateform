"""
Backlog stream exception module.

This module defines the BacklogStreamException, raised when an error occurs
during streaming execution of the backlog generation workflow, such as failures
in real-time response streaming, tool-call orchestration during streaming,
or unexpected runtime issues in the backlog pipeline.
"""

from backend.src.domain.exceptions.base.app_exception import AppException


class BacklogStreamException(AppException):
    """
    Exception raised when a backlog streaming operation fails.

    This exception is used to indicate failures occurring during streaming
    of backlog generation processes, including interrupted streams, tool
    execution failures during streaming, or unexpected runtime errors while
    delivering incremental backlog responses.

    Attributes:
        message (str): Human-readable error message describing the streaming failure.
        code (str): Internal error code identifying backlog streaming errors.
        http_status (int): HTTP status code returned to the client.
    """

    def __init__(self, message: str = "Backlog generation failed. Please try again."):
        """
        Initialize a backlog stream exception.

        Args:
            message (str): Error message describing the streaming failure.
        """
        super().__init__(
            message=message,
            code="BACKLOG_STREAM_ERROR",
            http_status=503,
        )