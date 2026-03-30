"""
JWT authentication middleware for FastAPI routes.

This module defines JWTAuthMiddleware, which protects all routes except public endpoints by verifying JWT tokens in the Authorization header.

Classes:
    JWTAuthMiddleware: Middleware to enforce JWT authentication on protected routes.
"""

import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from backend.src.domain.exceptions.invalid_token_exception import InvalidTokenException
from backend.src.infrastructure.di.container import Container

logger = logging.getLogger(__name__)


PUBLIC_PATHS = {
    "/auth/login",
    "/auth/refresh",
    "/docs",
    "/openapi.json",
    "/redoc",
}


class JWTAuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware to protect all routes with JWT.
    """

    async def dispatch(self, request: Request, call_next):
        """
        Intercept requests and enforce JWT authentication on protected routes.

        Args:
            request (Request): The incoming FastAPI request.
            call_next (Callable): The next middleware or route handler.

        Returns:
            JSONResponse or Response: The response object, either an error or the result of the next handler.

        Raises:
            InvalidTokenException: If the JWT token is missing, malformed, or invalid (handled and returned as 401 response).
        """
        if request.url.path in PUBLIC_PATHS:
            return await call_next(request)

        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            logger.warning("[Auth] Missing or malformed Authorization header: %s.", request.url.path)
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"error": {"code": "UNAUTHORIZED", "message": "Missing or invalid Authorization header."}},
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = auth_header.split(" ")[1]

        try:
            session = request.app.state.db.get_session()
            try:
                container = Container(session)
                payload = container.jwt_handler.verify_token(token)
                request.state.current_member = payload
                logger.info("[Auth] Token verified (member_id=%s).", payload.get("sub"))
            finally:
                session.close()

        except InvalidTokenException as e:
            logger.warning("[Auth] Invalid token on %s: %s.", request.url.path, str(e))
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"error": {"code": "INVALID_TOKEN", "message": str(e)}},
                headers={"WWW-Authenticate": "Bearer"},
            )

        return await call_next(request)