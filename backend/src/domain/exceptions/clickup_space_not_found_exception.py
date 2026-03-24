from backend.src.domain.exceptions.app_exception import AppException


class ClickUpSpaceNotFoundException(AppException):
    def __init__(self, space_id: str | int):
        super().__init__(
            message=f"ClickUp space not found: {space_id}",
            code="CLICKUP_SPACE_NOT_FOUND",
            http_status=404
        )