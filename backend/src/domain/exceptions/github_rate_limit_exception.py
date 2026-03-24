from backend.src.domain.exceptions.app_exception import AppException


class GitHubRateLimitException(AppException):
    def __init__(self, reset_time: str = None):
        msg = "GitHub API rate limit exceeded."
        if reset_time:
            msg += f" Please retry after {reset_time} UTC."
        super().__init__(
            message=msg,
            code="GITHUB_RATE_LIMIT",
            http_status=429
        )