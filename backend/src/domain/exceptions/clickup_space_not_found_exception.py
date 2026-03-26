from backend.src.domain.exceptions.app_exception import AppException


class ClickUpSpaceNotFoundException(AppException):
    def __init__(self, message="ClickUp space not found with ID/SPACE_CODE"):
        super().__init__(
            message=message,
            code="CLICKUP_SPACE_NOT_FOUND",
            http_status=404
        )