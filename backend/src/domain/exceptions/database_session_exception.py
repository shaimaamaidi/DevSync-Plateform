from backend.src.domain.exceptions.app_exception import AppException


class DatabaseSessionException(AppException):
    def __init__(self):
        super().__init__(
            message="Failed to create or retrieve database session",
            code="DB_SESSION_ERROR",
            http_status=500
        )