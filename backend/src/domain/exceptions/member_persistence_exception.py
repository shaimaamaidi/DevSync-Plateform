from backend.src.domain.exceptions.app_exception import AppException


class MemberPersistenceException(AppException):
    def __init__(self, msg: str = "Error occurred while accessing member data"):
        super().__init__(
            message=msg,
            code="MEMBER_PERSISTENCE_ERROR",
            http_status=500
        )