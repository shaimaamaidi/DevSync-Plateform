"""
Prompt file not found exception.

This module defines the PromptFileNotFoundException, raised when a prompt template
file cannot be found in the templates directory. It is triggered when the system
attempts to load a `.prompty` file that does not exist or is not accessible.
"""

from backend.src.domain.exceptions.base.app_exception import AppException


class PromptFileNotFoundException(AppException):
    """
    Exception raised when a prompt file is not found.

    This exception is used when the system attempts to load a prompt template file
    that does not exist in the expected templates directory or cannot be located.

    Attributes:
        message (str): Human-readable error message describing the missing file.
        code (str): Internal error code identifying the file-not-found error.
        http_status (int): HTTP status code returned to the client.
    """

    def __init__(self, message: str = "Prompt file not found."):
        """
        Initialize a PromptFileNotFoundException.

        Args:
            message (str): Error message describing the missing prompt file.
        """
        super().__init__(
            message=message,
            code="PROMPT_FILE_NOT_FOUND",
            http_status=500,
        )