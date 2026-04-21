"""
Stream cancelled exception.

This module defines the StreamCancelledException, raised when a streaming
operation is intentionally cancelled before completion.

It is used in streaming pipelines to signal that the process was terminated
by the client, orchestrator, or runtime control mechanism.
"""

from backend.src.domain.exceptions.app_exception import AppException


class StreamCancelledException(AppException):
    """
    Exception raised when a streaming process is cancelled.

    This exception is used when:
    - The client disconnects during streaming
    - The orchestrator cancels the stream execution
    - The runtime explicitly stops the stream before completion

    Attributes:
        message (str): Human-readable description of the cancellation reason.
        code (str): Internal error code identifying the cancellation event.
        http_status (int): HTTP status code returned to the client (typically 499).
    """

    def __init__(self, message: str = "Stream was cancelled."):
        """
        Initialize a StreamCancelledException.

        Args:
            message (str): Optional message describing why the stream was cancelled.
        """
        super().__init__(
            message=message,
            code="STREAM_CANCELLED",
            http_status=499
        )