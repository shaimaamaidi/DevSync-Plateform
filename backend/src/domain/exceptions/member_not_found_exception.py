from backend.src.domain.exceptions.app_exception import AppException


class MemberNotFoundException(AppException):
    def __init__(self, message=f"Member not found with ID/email"):
        super().__init__(
            message=message,
            code="MEMBER_NOT_FOUND",
            http_status=404
        )
