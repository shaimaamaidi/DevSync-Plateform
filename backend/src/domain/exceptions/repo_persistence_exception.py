"""Repository persistence exception."""

from backend.src.domain.exceptions.app_exception import AppException


class RepoPersistenceException(AppException):
    """Raised when repository persistence fails."""
    def __init__(self, msg: str = "Error occurred while accessing repository data"):
        """Initialize a repository persistence exception.

        Args:
            msg: Error message override.
        """
        super().__init__(
            message=msg,
            code="REPO_PERSISTENCE_ERROR",
            http_status=500
        )