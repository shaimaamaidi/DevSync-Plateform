from backend.src.domain.exceptions.app_exception import AppException


class DatabaseConnectionException(AppException):
    def __init__(self):
        super().__init__(
            message="Failed to connect to the database",
            code="DB_CONNECTION_ERROR",
            http_status=500
        )