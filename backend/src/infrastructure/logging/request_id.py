import logging
from contextvars import ContextVar

_REQUEST_ID_CTX = ContextVar("request_id", default="-")


def set_request_id(request_id: str) -> None:
    _REQUEST_ID_CTX.set(request_id)


def clear_request_id() -> None:
    _REQUEST_ID_CTX.set("-")


def get_request_id() -> str:
    return _REQUEST_ID_CTX.get()


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = get_request_id()
        return True
