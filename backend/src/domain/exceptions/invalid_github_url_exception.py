"""
Invalid GitHub URL exception.

This module defines the InvalidGitHubUrlException, raised when a GitHub URL fails validation.
"""

from backend.src.domain.exceptions.app_exception import AppException


class InvalidGitHubUrlException(AppException):
    """
    Exception raised when a GitHub URL fails validation.

    Args:
        url: GitHub URL that failed validation.
    """
    def __init__(self, url: str):
        """Initialize an invalid GitHub URL exception.

        Args:
            url: GitHub URL that failed validation.
        """
        super().__init__(
            message=f"Invalid GitHub URL: {url}",
            code="INVALID_GITHUB_URL",
            http_status=400
        )