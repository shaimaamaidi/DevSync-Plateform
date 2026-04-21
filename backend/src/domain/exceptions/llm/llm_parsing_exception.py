"""
LLM parsing exception module.

This module defines the LLMParsingException, which is raised when an LLM call
fails or when its response cannot be correctly parsed into the expected format.

It is used in LLM-driven pipelines to clearly separate parsing/LLM failures
from infrastructure or domain errors.
"""

from backend.src.domain.exceptions.base.app_exception import AppException


class LLMParsingException(AppException):
    """
    Exception raised when an LLM call or response parsing fails.

    This exception is typically used when:
    - The LLM response is malformed or incomplete
    - JSON decoding of the LLM output fails
    - The response does not match the expected schema
    - The agent returns invalid structured data

    Attributes:
        message (str): Human-readable description of the error.
        code (str): Internal error code identifying the failure type.
        http_status (int): HTTP status code returned to the client.
    """

    def __init__(self, agent_name: str, reason: str):
        """
        Initialize an LLM parsing exception.

        Args:
            agent_name (str): Name of the agent that triggered the failure.
            reason (str): Detailed reason explaining why parsing failed.
        """
        super().__init__(
            message=f"LLM call failed in {agent_name}: {reason}",
            code="LLM_PARSING_ERROR",
            http_status=502
        )