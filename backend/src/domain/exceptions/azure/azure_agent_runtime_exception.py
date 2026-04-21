"""
Azure agent runtime exception.

This module defines the AzureAgentRuntimeException, raised when an operation related to the
Azure agent runtime fails, such as connection issues, API errors, or runtime execution failures.
"""

from backend.src.domain.exceptions.base.app_exception import AppException


class AzureAgentRuntimeException(AppException):
    """
    Exception raised when an Azure agent runtime operation fails.

    This exception is used to signal failures occurring during interactions with the Azure agent runtime,
    including communication issues, service unavailability, or unexpected runtime errors.

    Attributes:
        message (str): Human-readable error message.
        code (str): Internal error code identifying the failure type.
        http_status (int): HTTP status code returned to the client.
    """

    def __init__(self, message: str = "Azure agent runtime operation failed."):
        """
        Initialize an Azure agent runtime exception.

        Args:
            message (str): Human-readable error message describing the failure.
        """
        super().__init__(
            message=message,
            code="AZURE_AGENT_RUNTIME_ERROR",
            http_status=502
        )