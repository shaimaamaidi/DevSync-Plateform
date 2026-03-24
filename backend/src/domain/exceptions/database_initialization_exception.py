from backend.src.domain.exceptions.app_exception import AppException


class DatabaseInitializationException(AppException):
    def __init__(self, msg: str = "Failed to initialize or create the database"):
        super().__init__(
            message=msg,
            code="DB_INIT_ERROR",
            http_status=500
        )