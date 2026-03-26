"""Repository not found exception."""

from backend.src.domain.exceptions.app_exception import AppException


class RepoNotFoundException(AppException):
    """Raised when a repository cannot be found."""
    def __init__(self, message=f"Repository not found with ID/URL/Name"):
        """Initialize a repository not found exception.

        Args:
            message: Error message override.
        """
        super().__init__(
            message=message,
            code="REPO_NOT_FOUND",
            http_status=404
        )