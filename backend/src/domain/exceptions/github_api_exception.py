from backend.src.domain.exceptions.app_exception import AppException

class GitHubApiException(AppException):
    """
    Exception raised for errors during GitHub API requests.

    Attributes:
        message (str): Human readable error message.
        code (str): Stable error code for GitHub API errors.
        http_status (int): HTTP status to return.
    """
    def __init__(self, message: str, code: str = "GITHUB_API_ERROR", http_status: int = 502):
        """
        Initialize a GitHub API exception.

        Args:
            message (str): Human readable error message.
            code (str): Stable error code (default: 'GITHUB_API_ERROR').
            http_status (int): HTTP status to return (default: 502 Bad Gateway).
        """
        super().__init__(message=message, code=code, http_status=http_status)