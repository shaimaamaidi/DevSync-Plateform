"""GitHub repository not found exception."""

from backend.src.domain.exceptions.app_exception import AppException


class GitHubRepoNotFoundException(AppException):
    """Raised when a GitHub repository cannot be found."""
    def __init__(self, repo_url: str):
        """Initialize a repository not found exception.

        Args:
            repo_url: GitHub repository URL.
        """
        super().__init__(
            message=f"GitHub repository not found: {repo_url}",
            code="GITHUB_REPO_NOT_FOUND",
            http_status=404
        )