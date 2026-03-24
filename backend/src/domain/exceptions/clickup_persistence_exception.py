from backend.src.domain.exceptions.app_exception import AppException


class ClickUpPersistenceException(AppException):
    def __init__(self, msg: str = "Error occurred while accessing ClickUp space data"):
        super().__init__(
            message=msg,
            code="CLICKUP_PERSISTENCE_ERROR",
            http_status=500
        )