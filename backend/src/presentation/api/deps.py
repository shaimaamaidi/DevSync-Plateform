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
        Exception: For any other unexpected errors during container creation.
    """
    session = request.app.state.db.get_session()
    try:
        yield Container(session)
    except AppException:
        raise
    except Exception as e:
        logger.error(
            "Error while creating container for request: %s.",
            str(e),
            exc_info=e,
        )
        raise
    finally:
        session.close()
