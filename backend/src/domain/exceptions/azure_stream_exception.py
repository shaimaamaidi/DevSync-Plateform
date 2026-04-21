"""
Azure stream exception module.

This module defines the AzureStreamException, raised when an error occurs during
Azure AI Agent streaming execution, such as failures in event streaming,
response chunk processing, or communication with Azure runtime services.
"""

from backend.src.domain.exceptions.app_exception import AppException


class AzureStreamException(AppException):
    """
    Exception raised when an Azure AI Agent streaming operation fails.

    This exception is used to indicate failures occurring during streaming
    execution of Azure AI Agents, including issues such as interrupted streams,
    failed event processing, or unexpected runtime errors in the streaming pipeline.

    Attributes:
        message (str): Human-readable error message describing the streaming failure.
        code (str): Internal error code identifying Azure stream errors.
        http_status (int): HTTP status code returned to the client.
    """

    def __init__(self, message: str = "Azure streaming operation failed."):
        """
        Initialize an Azure stream exception.

        Args:
            message (str): Error message describing the streaming failure.
        """
        super().__init__(
            message=message,
            code="AZURE_STREAM_ERROR",
            http_status=500,
        )