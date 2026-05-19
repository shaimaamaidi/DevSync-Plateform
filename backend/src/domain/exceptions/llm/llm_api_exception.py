"""
LLM API exception.

This module defines the LLMApiException, raised when an external Large Language Model
(LLM) API request fails during agent execution.

The exception is used to wrap upstream API failures and provide a consistent
application-level error structure for infrastructure and service layers.
"""

from backend.src.domain.exceptions.base.app_exception import AppException


class LLMApiException(AppException):
    """
    Exception raised when an external LLM API call fails.

    This exception is used when an agent encounters an error while communicating
    with a Large Language Model provider API, such as invalid responses,
    upstream service failures, or unavailable endpoints.

    Attributes:
        message (str): Human-readable error message describing the API failure.
        code (str): Internal error code identifying the LLM API error.
        http_status (int): HTTP status code returned to the client.
    """

    def __init__(self, agent_name: str, status_code: int, reason: str):
        """
        Initialize an LLMApiException.

        Args:
            agent_name (str): Name of the agent that triggered the LLM API request.
            status_code (int): HTTP status code returned by the external API.
            reason (str): Detailed reason describing the API failure.
        """
        super().__init__(
            message=f"LLM API error in agent '{agent_name}' (HTTP {status_code}): {reason}",
            code="LLM_API_ERROR",
            http_status=502,
        )