"""
Prompt templates directory not found exception.

This module defines the PromptTemplateDirectoryNotFoundException, raised when the
system cannot locate the directory containing `.prompty` template files required
for prompt loading and rendering.
"""

from backend.src.domain.exceptions.app_exception import AppException


class PromptTemplateDirectoryNotFoundException(AppException):
    """
    Exception raised when the prompt templates directory is not found.

    This exception is used when the application fails to locate the directory
    that contains `.prompty` files required for loading and rendering prompts.

    Attributes:
        message (str): Human-readable error message describing the missing directory.
        code (str): Internal error code identifying the configuration error.
        http_status (int): HTTP status code returned to the client.
    """

    def __init__(self, message: str = "Prompt templates directory not found."):
        """
        Initialize a PromptTemplateDirectoryNotFoundException.

        Args:
            message (str): Error message describing the missing templates directory.
        """
        super().__init__(
            message=message,
            code="PROMPT_TEMPLATES_DIR_NOT_FOUND",
            http_status=500,
        )