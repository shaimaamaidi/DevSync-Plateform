from backend.src.domain.exceptions.app_exception import AppException


class MemberNotFoundException(AppException):
    def __init__(self, member_id: int | str):
        super().__init__(
            message=f"Member not found with ID/email: {member_id}",
            code="MEMBER_NOT_FOUND",
            http_status=404
        )
