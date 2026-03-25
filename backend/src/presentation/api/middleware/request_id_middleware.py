import uuid
from fastapi import Request

from backend.src.infrastructure.logging.request_id import clear_request_id, set_request_id


async def request_id_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-Id") or str(uuid.uuid4())
    set_request_id(request_id)
    try:
        response = await call_next(request)
        response.headers["X-Request-Id"] = request_id
        return response
    finally:
        clear_request_id()
