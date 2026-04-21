"""
Service unavailable exception.

This module defines the ServiceUnavailableException, raised when a required
application service is not available or cannot be accessed at runtime.

It is typically used to signal infrastructure or dependency availability issues
such as missing initialization, failed startup, or temporary service downtime.
"""

from backend.src.domain.exceptions.base.app_exception import AppException


class ServiceUnavailableException(AppException):
    """
    Exception raised when a required service is unavailable.

    This exception is used when:
    - A required application service has not been initialized
    - A dependency is temporarily unavailable
    - A runtime component cannot be accessed due to infrastructure issues

    Attributes:
        message (str): Human-readable description of the error.
        code (str): Internal error code identifying the service failure type.
        http_status (int): HTTP status code returned to the client.
    """

    def __init__(self, message: str = "Service is currently unavailable."):
        """
        Initialize a ServiceUnavailableException.

        Args:
            message (str): Description of why the service is unavailable.
        """
        super().__init__(
            message=message,
            code="SERVICE_UNAVAILABLE",
            http_status=500
        )