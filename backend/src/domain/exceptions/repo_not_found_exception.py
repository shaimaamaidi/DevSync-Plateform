from backend.src.domain.exceptions.app_exception import AppException


class RepoNotFoundException(AppException):
    def __init__(self, repo_id: int | str):
        super().__init__(
            message=f"Repository not found with ID/URL: {repo_id}",
            code="REPO_NOT_FOUND",
            http_status=404
        )