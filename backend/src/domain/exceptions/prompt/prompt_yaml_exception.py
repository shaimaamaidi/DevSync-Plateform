"""
Prompt YAML exception.

This module defines the PromptYamlException, raised when a `.prompty` file
contains invalid YAML or cannot be parsed correctly. It is triggered when the
system fails to deserialize the prompt file into a valid structure.
"""

from backend.src.domain.exceptions.base.app_exception import AppException


class PromptYamlException(AppException):
    """
    Exception raised when a prompt YAML file is invalid.

    This exception is used when the system cannot parse a `.prompty` file due to
    malformed YAML syntax, corrupted content, or deserialization failures.

    Attributes:
        message (str): Human-readable error message describing the YAML failure.
        code (str): Internal error code identifying the YAML parsing error.
        http_status (int): HTTP status code returned to the client.
    """

    def __init__(self, message: str = "Invalid prompt YAML file."):
        """
        Initialize a PromptYamlException.

        Args:
            message (str): Error message describing the YAML parsing failure.
        """
        super().__init__(
            message=message,
            code="PROMPT_YAML_ERROR",
            http_status=500,
        )