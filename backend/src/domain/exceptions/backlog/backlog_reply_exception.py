"""
Backlog reply exception module.

This module defines the BacklogReplyException, raised when an error occurs
during the processing of a backlog verification or reply workflow, such as
invalid state handling, failed validation loops, or unexpected runtime issues
while updating or confirming backlog changes.
"""

from backend.src.domain.exceptions.base.app_exception import AppException


class BacklogReplyException(AppException):
    """
    Exception raised when a backlog reply or verification process fails.

    This exception is used to indicate failures occurring during backlog
    review or reply workflows, including invalid transitions in the verification
    loop, processing errors, or unexpected runtime issues while handling user
    feedback on backlog data.

    Attributes:
        message (str): Human-readable error message describing the failure.
        code (str): Internal error code identifying the backlog reply error.
        http_status (int): HTTP status code returned to the client.
    """

    def __init__(self, message: str = "Backlog reply processing failed."):
        """
        Initialize a backlog reply exception.

        Args:
            message (str): Error message describing the backlog reply failure.
        """
        super().__init__(
            message=message,
            code="BACKLOG_REPLY_ERROR",
            http_status=500,
        )