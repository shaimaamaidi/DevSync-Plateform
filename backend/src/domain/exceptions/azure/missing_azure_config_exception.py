"""
Missing Azure configuration exception.

This module defines the MissingAzureConfigException, raised when one or more Azure-related
environment variables are missing from the application configuration.

It specializes MissingEnvVariableException to handle Azure-specific configuration issues.
"""

from backend.src.domain.exceptions.common.missing_env_variable_exception import MissingEnvVariableException


class MissingAzureConfigException(MissingEnvVariableException):
    """
    Exception raised when an Azure-specific environment variable is missing.

    This exception is used when required Azure configuration values are not present
    in the environment, preventing proper initialization of Azure-dependent components
    such as agents, storage, or API clients.

    Attributes:
        message (str): Human-readable error message describing the missing configuration.
        code (str): Internal error code identifying the configuration error type.
        http_status (int): HTTP status code returned to the client (inherited from parent).
    """

    def __init__(self, message: str = "Missing Azure configuration."):
        """
        Initialize a MissingAzureConfigException.

        Args:
            message (str): Error message describing the missing Azure configuration.
        """
        super().__init__(message)
        self.code = "MISSING_AZURE_CONFIG"