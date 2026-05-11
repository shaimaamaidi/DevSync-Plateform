from backend.src.domain.exceptions.base.app_exception import AppException


class ClickUpSpaceNameMismatchException(AppException):
    def __init__(self, expected: str, actual: str):
        super().__init__(
            message=f"Space name mismatch: expected '{expected}', got '{actual}'.",
            code="CLICKUP_SPACE_NAME_MISMATCH",
            http_status=409,
        )