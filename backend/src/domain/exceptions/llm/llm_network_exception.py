from backend.src.domain.exceptions.base.app_exception import AppException


class LLMNetworkException(AppException):
    def __init__(self, agent_name: str, reason: str):
        super().__init__(
            message=f"Network error while contacting LLM in agent '{agent_name}': {reason}",
            code="LLM_NETWORK_ERROR",
            http_status=502
        )