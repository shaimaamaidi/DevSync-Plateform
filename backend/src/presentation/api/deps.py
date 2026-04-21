"""
FastAPI dependency providers.

This module defines dependency injection providers used by FastAPI routes.
It is responsible for building request-scoped infrastructure objects such as
the DI container and exposing application use cases initialized at startup.

Functions:
    get_container: Provides a request-scoped dependency injection container.
    get_backlog_use_case: Provides the backlog generation use case instance.
"""

import logging
from typing import Generator

from fastapi import Request

from backend.src.application.use_cases.generate_backlog_use_case import GenerateBacklogUseCase
from backend.src.domain.exceptions.base.app_exception import AppException
from backend.src.domain.exceptions.system.service_unavailable_exception import ServiceUnavailableException
from backend.src.infrastructure.di.container import Container


logger = logging.getLogger(__name__)


def get_container(request: Request) -> Generator[Container, None, None]:
    """
    Provide a request-scoped dependency injection container.

    This function creates a new DI container per incoming HTTP request.
    It ensures that all services using database sessions or request-bound
    resources are properly isolated and safely disposed of after the request.

    Lifecycle:
        - Retrieve DB session from application state
        - Initialize DI container with session
        - Yield container to FastAPI route
        - Close session after request completion

    Args:
        request (Request):
            The incoming FastAPI request object.

    Yields:
        Container:
            A request-scoped dependency injection container configured with
            a database session and application services.

    Raises:
        AppException:
            Re-raised if a known application-level exception occurs during
            container initialization or usage.

        Exception:
            Unexpected runtime errors during container creation or dependency
            resolution.

    Notes:
        - Each request gets its own isolated database session.
        - The session is automatically closed after request completion.
        - This ensures thread-safety and avoids shared state issues.
    """
    logger.info("Creating DI container for request: %s", request.url.path)

    session = request.app.state.db.get_session()
    try:
        yield Container(session)
    except AppException:
        raise
    except Exception as e:
        logger.exception(
            "Error while creating container for request: %s.",
            str(e),
        )
        raise
    finally:
        session.close()

        logger.info("Closed DI container for request: %s", request.url.path)

def get_backlog_use_case(request: Request) -> GenerateBacklogUseCase:
    """
    Retrieve the backlog generation use case instance.

    This dependency provides access to a singleton instance of the
    backlog generation use case, initialized at application startup.
    It is not request-scoped and does not create new instances per call.

    Args:
        request (Request):
            The incoming FastAPI request object.

    Returns:
        GenerateBacklogUseCase:
            The initialized backlog generation use case responsible for
            orchestrating the full backlog generation workflow.

    Raises:
        ServiceUnavailableException: If the backlog generation use case is not initialized
            in the application state or cannot be retrieved.
        Exception: If an unexpected runtime error occurs while accessing the application state
            or resolving the use case dependency.

    Notes:
        - This use case is stored in `app.state.backlog_container`.
        - It is initialized once at startup to improve performance.
        - It should NOT be modified per request.
    """
    try:
        use_case = request.app.state.backlog_container.generate_backlog_use_case

        if use_case is None:
            raise ServiceUnavailableException("Backlog use case is not initialized.")

        return use_case

    except ServiceUnavailableException:
        raise

    except Exception as e:
        logger.exception("Failed to retrieve backlog use case: %s", str(e))
        raise ServiceUnavailableException("Backlog service is unavailable.") from e