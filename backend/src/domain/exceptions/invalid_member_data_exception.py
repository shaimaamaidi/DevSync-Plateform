from backend.src.domain.exceptions.app_exception import AppException


class InvalidMemberDataException(AppException):
    def __init__(self, missing_fields: list[str], data: dict = None):
        fields = ", ".join(missing_fields)
        detail = f" — received: {data}" if data else ""
        super().__init__(
            message=f"Invalid member data, missing required fields: {fields}{detail}",
            code="INVALID_MEMBER_DATA",
            http_status=400
        )