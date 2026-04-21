"""
Prompt file read exception.

This module defines the PromptFileReadException, raised when an input/output (I/O)
error occurs while reading a `.prompty` template file from the filesystem. It is
triggered when the system is unable to access or properly read the prompt file.
"""

from backend.src.domain.exceptions.base.app_exception import AppException


class PromptFileReadException(AppException):
    """
    Exception raised when a prompt file cannot be read.

    This exception is used when the system fails to read a prompt template file
    due to filesystem errors, permission issues, or unexpected I/O failures.

    Attributes:
        message (str): Human-readable error message describing the read failure.
        code (str): Internal error code identifying the file-read error.
        http_status (int): HTTP status code returned to the client.
    """

    def __init__(self, message: str = "Failed to read prompt file from filesystem."):
        """
        Initialize a PromptFileReadException.

        Args:
            message (str): Error message describing the file read failure.
        """
        super().__init__(
            message=message,
            code="PROMPT_FILE_READ_ERROR",
            http_status=500,
        )