"""
Request ID middleware for FastAPI.

This module provides middleware to attach a unique request ID to each incoming request and response, enabling traceability across logs and distributed systems.

Functions:
    request_id_middleware: Middleware to set and clear request IDs for each request.
"""

import uuid
from fastapi import Request

from backend.src.infrastructure.logging.request_id import clear_request_id, set_request_id


async def request_id_middleware(request: Request, call_next):
    """
    Attach a request ID to the context and response.

    Args:
        request (Request): The incoming FastAPI request.
        call_next (Callable): The next middleware or route handler.

    Returns:
        Response: The response object with an X-Request-Id header.

    Raises:
        Exception: Any exception raised by downstream middleware or handlers (not handled here).
    """
    request_id = request.headers.get("X-Request-Id") or str(uuid.uuid4())
    set_request_id(request_id)

    try:
        response = await call_next(request)
        response.headers["X-Request-Id"] = request_id
        return response
    finally:
        clear_request_id()
