"""
Invalid GitHub URL exception.

This module defines the InvalidGitHubUrlException, raised when a provided GitHub URL
does not match the expected format or fails validation rules.
"""

from backend.src.domain.exceptions.app_exception import AppException


class InvalidGitHubUrlException(AppException):
    """
    Exception raised when a GitHub URL is invalid.

    This exception is used when the provided GitHub repository URL does not conform
    to expected validation rules or is malformed, preventing further processing.

    Attributes:
        message (str): Human-readable error message describing the invalid URL.
        code (str): Internal error code identifying the validation error.
        http_status (int): HTTP status code returned to the client.
    """

    def __init__(self, url: str):
        """
        Initialize an InvalidGitHubUrlException.

        Args:
            url (str): GitHub URL that failed validation.
        """
        super().__init__(
            message=f"Invalid GitHub URL: {url}",
            code="INVALID_GITHUB_URL",
            http_status=400,
        )