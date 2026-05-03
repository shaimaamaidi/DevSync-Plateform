"""
Agent initialization exception.

This module defines the AgentInitializationException, raised when an LLM agent fails
to initialize due to missing configuration, invalid setup, or client initialization errors.
"""

from backend.src.domain.exceptions.base.app_exception import AppException


class AgentInitializationException(AppException):
    """
    Exception raised when an LLM agent initialization fails.

    This exception is used to signal failures occurring during the initialization
    of an LLM agent, such as missing configuration, invalid parameters, or errors
    during client setup (e.g., Azure/OpenAI client instantiation).

    Attributes:
        message (str): Human-readable error message describing the failure.
        code (str): Internal error code identifying the failure type.
        http_status (int): HTTP status code returned to the client.
    """

    def __init__(self, message: str = "Agent initialization failed."):
        """
        Initialize an agent initialization exception.

        Args:
            message (str): Human-readable error message describing the failure.
        """
        super().__init__(
            message=message,
            code="AGENT_INITIALIZATION_ERROR",
            http_status=500,
        )