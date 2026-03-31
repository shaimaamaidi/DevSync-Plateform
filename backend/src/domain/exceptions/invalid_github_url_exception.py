"""
Invalid GitHub URL exception.

This module defines the InvalidGitHubUrlException, raised when a GitHub URL fails validation.
"""

from backend.src.domain.exceptions.app_exception import AppException


class InvalidGitHubUrlException(AppException):
    """
    Exception raised when a GitHub URL fails validation.

    Attributes:
        message (str): Error message override.
        code (str): Error code.
        http_status (int): HTTP status to return.
    """
    def __init__(self, url: str):
        """
        Initialize an invalid GitHub URL exception.

        Args:
            url (str): GitHub URL that failed validation.
        """
        super().__init__(
            message=f"Invalid GitHub URL: {url}",
            code="INVALID_GITHUB_URL",
            http_status=400
        )