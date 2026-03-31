"""
FastAPI dependency providers.

This module defines dependency providers for FastAPI routes, including request-scoped containers.

Functions:
    get_container: Provides a request-scoped dependency injection container.
"""

import logging
from typing import Generator

from fastapi import Request

from backend.src.domain.exceptions.app_exception import AppException
from backend.src.infrastructure.di.container import Container


logger = logging.getLogger(__name__)


def get_container(request: Request) -> Generator[Container, None, None]:
    """
    Provide a request-scoped container.

    Args:
        request (Request): The incoming FastAPI request.

    Yields:
        Container: Configured with the request session.

    Raises:
        AppException: If a known application exception occurs (propagated).
        Exception: For unexpected errors during container creation.
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
