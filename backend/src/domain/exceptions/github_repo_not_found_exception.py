from backend.src.domain.exceptions.app_exception import AppException


class GitHubRepoNotFoundException(AppException):
    def __init__(self, repo_url: str):
        super().__init__(
            message=f"GitHub repository not found: {repo_url}",
            code="GITHUB_REPO_NOT_FOUND",
            http_status=404
        )