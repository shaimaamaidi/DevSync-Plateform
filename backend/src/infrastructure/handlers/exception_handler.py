"""
FastAPI exception handlers for domain errors.

This module provides centralized exception handling for FastAPI applications, mapping domain and validation errors to structured JSON responses and logging them appropriately.

Classes:
    FastAPIExceptionHandler: Static methods for handling domain, validation, and generic exceptions in FastAPI.
"""

import logging
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from backend.src.domain.exceptions.base.app_exception import AppException


logger = logging.getLogger(__name__)


_NOT_FOUND_CODES = {
    "CLICKUP_SPACE_NOT_FOUND",
    "MEMBER_NOT_FOUND",
    "REPO_NOT_FOUND",
}

_PERSISTENCE_CODES = {
    "CLICKUP_PERSISTENCE_ERROR",
    "MEMBER_PERSISTENCE_ERROR",
    "REPO_PERSISTENCE_ERROR",
    "DATABASE_CONNECTION_ERROR",
    "DATABASE_INITIALIZATION_ERROR",
    "DATABASE_SESSION_ERROR",
    "REFRESH_TOKEN_PERSISTENCE_ERROR",
}

_VALIDATION_CODES = {
    "INVALID_INPUT",
    "INVALID_MEMBER_DATA",
    "INVALID_GITHUB_URL",
}

_GITHUB_CODES = {
    "GITHUB_RATE_LIMIT",
    "GITHUB_API_ERROR",
    "GITHUB_REPO_NOT_FOUND",
}

_AUTH_CODES = {
    "INVALID_TOKEN",
    "MISSING_ENV_VARIABLE",
}

_AZURE_CODES = {
    "MISSING_AZURE_CONFIG",
    "AZURE_AGENT_RUNTIME_ERROR",
    "AZURE_STREAM_ERROR",
    "TOOL_PARSING_ERROR",
    "TOOL_EXECUTION_ERROR",
    "INVALID_TOOL_ARGUMENT",
    "STREAM_CANCELLED",
    "STREAM_EXECUTION_ERROR"
}

_PROMPT_CODES = {
    "PROMPT_RENDER_ERROR",
    "PROMPT_FILE_READ_ERROR",
    "PROMPT_FILE_NOT_FOUND",
    "PROMPT_YAML_ERROR",
    "PROMPT_SCHEMA_ERROR",
    "PROMPT_TEMPLATES_DIR_NOT_FOUND",
}

_BACKLOG_CODES = {
    "BACKLOG_GENERATION_ERROR",
    "LLM_PARSING_ERROR",
    "BACKLOG_REPLY_ERROR",
    "REPLY_STREAM_ERROR",
    "BACKLOG_STREAM_ERROR",
    "SERVICE_UNAVAILABLE",

}


class FastAPIExceptionHandler:
    """
    Centralized exception handling for FastAPI.

    Provides static methods to handle domain-specific, validation, and generic exceptions, returning JSON responses and logging errors.
    """

    @staticmethod
    async def handle_app_exception(request: Request, exc: AppException) -> JSONResponse:
        """
        Handle domain application exceptions.

        Args:
            request (Request): The incoming FastAPI request.
            exc (AppException): The domain application exception to handle.

        Returns:
            JSONResponse: JSON response with error code and message.

        Raises:
            AppException: If a domain-specific error occurs.
        """

        if exc.code in _NOT_FOUND_CODES:
            logger.warning(
                "Not Found Error [%s]: %s.",
                exc.code,
                exc.message,
            )
        elif exc.code in _PERSISTENCE_CODES:
            logger.error(
                "Persistence/Database Error [%s]: %s.",
                exc.code,
                exc.message,
                exc_info=exc
            )
        elif exc.code in _VALIDATION_CODES:
            logger.info(
                "Validation Error [%s]: %s.",
                exc.code,
                exc.message,
            )
        elif exc.code in _GITHUB_CODES:
            logger.warning(
                "GitHub API Error [%s]: %s.",
                exc.code,
                exc.message,
            )
        elif exc.code in _AUTH_CODES:
            logger.warning(
                "Auth Error [%s]: %s.",
                exc.code,
                exc.message,
            )
        elif exc.code in _AZURE_CODES:
            logger.error(
                "Azure Error [%s]: %s.",
                exc.code,
                exc.message,
                exc_info=exc,
            )
        elif exc.code in _PROMPT_CODES:
            logger.error(
                "Prompt Error [%s]: %s.",
                exc.code,
                exc.message,
                exc_info=exc,
            )
        elif exc.code in _BACKLOG_CODES:
            logger.error(
                "Backlog Generation Error [%s]: %s.",
                exc.code,
                exc.message,
                exc_info=exc,
            )
        else:
            logger.error(
                "Unknown Application Error [%s]: %s.",
                exc.code,
                exc.message,
                exc_info=exc
            )

        return JSONResponse(
            status_code=exc.http_status,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                }
            },
        )

    @staticmethod
    async def handle_validation_exception(request: Request, exc: RequestValidationError) -> JSONResponse:
        """
        Handle request validation errors.

        Args:
            request (Request): The incoming FastAPI request.
            exc (RequestValidationError): The validation exception to handle.

        Returns:
            JSONResponse: JSON response with validation error details.
        """
        logger.info(
            "Validation Error on request %s: %s.",
            request.url.path,
            exc.errors(),
        )
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Request validation failed",
                    "details": exc.errors(),
                }
            },
        )

    @staticmethod
    async def handle_generic_exception(request: Request, exc: Exception) -> JSONResponse:
        """
        Handle unexpected exceptions.

        Args:
            request (Request): The incoming FastAPI request.
            exc (Exception): The unexpected exception to handle.

        Returns:
            JSONResponse: JSON response with internal server error details.
        """
        logger.exception(
            "Unhandled exception on request %s: %s.",
            request.url.path,
            str(exc),
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "Internal server error",
                }
            },
        )