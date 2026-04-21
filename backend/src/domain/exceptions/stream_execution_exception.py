"""
Stream execution exception.

This module defines the StreamExecutionException, raised when an unexpected
error occurs during stream orchestration or execution.

It is used to signal failures in the streaming pipeline that are not caused
by client cancellation but by runtime or system-level errors.
"""

from backend.src.domain.exceptions.app_exception import AppException


class StreamExecutionException(AppException):
    """
    Exception raised when a stream execution fails unexpectedly.

    This exception is used when:
    - An internal error occurs during stream orchestration
    - The streaming pipeline crashes or fails mid-execution
    - A runtime or infrastructure issue interrupts processing

    Attributes:
        message (str): Human-readable description of the error.
        code (str): Internal error code identifying the execution failure type.
        http_status (int): HTTP status code returned to the client.
    """

    def __init__(self, message: str = "Unexpected stream execution failure."):
        """
        Initialize a StreamExecutionException.

        Args:
            message (str): Description of the stream execution failure.
        """
        super().__init__(
            message=message,
            code="STREAM_EXECUTION_ERROR",
            http_status=500
        )