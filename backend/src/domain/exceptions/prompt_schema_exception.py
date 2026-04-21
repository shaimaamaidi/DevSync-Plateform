"""
Prompt schema exception.

This module defines the PromptSchemaException, raised when a prompt structure
is syntactically valid YAML but does not respect the required schema. It is
triggered when required fields are missing or when the prompt format is invalid.
"""

from backend.src.domain.exceptions.app_exception import AppException


class PromptSchemaException(AppException):
    """
    Exception raised when a prompt schema is invalid.

    This exception is used when a `.prompty` file is valid YAML but does not
    conform to the expected prompt structure. It typically occurs when required
    fields are missing or incorrectly defined after YAML parsing.

    Attributes:
        message (str): Human-readable error message describing the schema failure.
        code (str): Internal error code identifying the schema validation error.
        http_status (int): HTTP status code returned to the client.
    """

    def __init__(self, message: str = "Invalid prompt schema: missing or incorrect required fields."):
        """
        Initialize a PromptSchemaException.

        Args:
            message (str): Error message describing the schema validation failure.
        """
        super().__init__(
            message=message,
            code="PROMPT_SCHEMA_ERROR",
            http_status=500,
        )