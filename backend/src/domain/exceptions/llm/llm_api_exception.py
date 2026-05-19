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

    def __init__(self):
        """
        Initialize an LLMApiException.
        """
        super().__init__(
            message="The AI service is currently unavailable. Please try again in a few moments.",
            code="LLM_API_ERROR",
            http_status=502,
        )