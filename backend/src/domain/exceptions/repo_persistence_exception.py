from backend.src.domain.exceptions.app_exception import AppException


class RepoPersistenceException(AppException):
    def __init__(self, msg: str = "Error occurred while accessing repository data"):
        super().__init__(
            message=msg,
            code="REPO_PERSISTENCE_ERROR",
            http_status=500
        )