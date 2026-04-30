"""
Missing ClickUp configuration exception.

This module defines the MissingClickUpConfigException, raised when one or more ClickUp-related
environment variables are missing from the application configuration.

It specializes MissingEnvVariableException to handle ClickUp-specific configuration issues.
"""

from backend.src.domain.exceptions.common.missing_env_variable_exception import MissingEnvVariableException


class MissingClickUpConfigException(MissingEnvVariableException):
    """
    Exception raised when a ClickUp-specific environment variable is missing.

    This exception is used when required ClickUp configuration values are not present
    in the environment, preventing proper initialization of ClickUp-dependent components
    such as API clients, workspace readers, or task writers.

    Attributes:
        message (str): Human-readable error message describing the missing configuration.
        code (str): Internal error code identifying the configuration error type.
        http_status (int): HTTP status code returned to the client (inherited from parent).
    """

    def __init__(self, message: str = "Missing ClickUp configuration."):
        """
        Initialize a MissingClickUpConfigException.

        Args:
            message (str): Error message describing the missing ClickUp configuration.
        """
        super().__init__(message)
        self.code = "MISSING_CLICKUP_CONFIG"