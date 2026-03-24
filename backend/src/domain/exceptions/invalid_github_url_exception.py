from backend.src.domain.exceptions.app_exception import AppException

class InvalidGitHubUrlException(AppException):
    def __init__(self, url: str):
        super().__init__(
            message=f"Invalid GitHub URL: {url}",
            code="INVALID_GITHUB_URL",
            http_status=400
        )