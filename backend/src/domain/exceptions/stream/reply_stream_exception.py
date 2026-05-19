"""
Reply stream exception.

This module defines the ReplyStreamException, raised when an error occurs during
streaming of reply generation (e.g., LLM streaming failure or interruption).

It is used in streaming pipelines to signal failures occurring while producing
incremental responses to the user.
"""

from backend.src.domain.exceptions.base.app_exception import AppException


class ReplyStreamException(AppException):
    """
    Exception raised when a reply streaming process fails.

    This exception is used when:
    - The streaming response from an LLM is interrupted
    - The stream cannot be initialized or consumed
    - An unexpected runtime error occurs during response streaming

    Attributes:
        message (str): Human-readable description of the error.
        code (str): Internal error code identifying the streaming failure type.
        http_status (int): HTTP status code returned to the client.
    """

    def __init__(self, message: str = "Failed to process your reply. Please try again."):
        """
        Initialize a ReplyStreamException.

        Args:
            message (str): Description of the streaming failure.
        """
        super().__init__(
            message=message,
            code="REPLY_STREAM_ERROR",
            http_status=500
        )