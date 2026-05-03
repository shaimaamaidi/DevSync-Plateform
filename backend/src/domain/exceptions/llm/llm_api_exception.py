from backend.src.domain.exceptions.base.app_exception import AppException


class LLMApiException(AppException):
    def __init__(self, agent_name: str, status_code: int, reason: str):
        super().__init__(
            message=f"LLM API error in agent '{agent_name}' (HTTP {status_code}): {reason}",
            code="LLM_API_ERROR",
            http_status=502
        )