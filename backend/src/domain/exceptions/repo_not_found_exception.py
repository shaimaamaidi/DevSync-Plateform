from backend.src.domain.exceptions.app_exception import AppException


class RepoNotFoundException(AppException):
    def __init__(self, message=f"Repository not found with ID/URL/Name"):
        super().__init__(
            message=message,
            code="REPO_NOT_FOUND",
            http_status=404
        )