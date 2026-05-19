"""
LLM network exception.

This module defines the LLMNetworkException, raised when a network-related failure
occurs while communicating with an external Large Language Model (LLM) API.

The exception is used to handle connectivity issues such as timeouts,
connection failures, or unreachable LLM services during agent execution.
"""

from backend.src.domain.exceptions.base.app_exception import AppException


class LLMNetworkException(AppException):
    """
    Exception raised when a network error occurs while contacting an LLM service.

    This exception is used when an agent cannot successfully communicate with
    an external Large Language Model provider due to connectivity or transport
    issues.

    Attributes:
        message (str): Human-readable error message describing the network failure.
        code (str): Internal error code identifying the LLM network error.
        http_status (int): HTTP status code returned to the client.
    """

    def __init__(self):
        """
        Initialize an LLMNetworkException.
        """
        super().__init__(
            message="Unable to reach the AI service due to a network issue. Please check your connection and try again.",
            code="LLM_NETWORK_ERROR",
            http_status=502,
        )