"""
Request id context utilities for logging.
"""

import logging
from contextvars import ContextVar


_REQUEST_ID_CTX = ContextVar("request_id", default="-")


def set_request_id(request_id: str) -> None:
    """
    Set the request id for the current context.

    Args:
        request_id (str): Request identifier string.

    Returns:
        None: The function sets the request ID in context but does not return anything.
    """
    _REQUEST_ID_CTX.set(request_id)

    

def clear_request_id() -> None:
    """
    Reset the request id context to the default value.
    """
    _REQUEST_ID_CTX.set("-")

def get_request_id() -> str:
    """
    Return the current request id.

    Returns:
        str: Request id string.
    """
    return _REQUEST_ID_CTX.get()

class RequestIdFilter(logging.Filter):
    """
    Inject request id into log records.
    """
    def filter(self, record: logging.LogRecord) -> bool:
        """
        Attach the request id to the record.

        Args:
            record (logging.LogRecord): Log record instance.

        Returns:
            bool: True to keep the record.
        """
        record.request_id = get_request_id()
    
        return True
        
