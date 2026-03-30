"""
FastAPI application factory.

This module defines the FastAPI application factory, including startup/shutdown events, middleware, exception handlers, and router registration.

Functions:
    lifespan: Async context manager for startup and shutdown events.
    create_app: Creates and configures the FastAPI application instance.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from backend.src.domain.exceptions.app_exception import AppException
from backend.src.infrastructure.handlers.exception_handler import FastAPIExceptionHandler
from backend.src.infrastructure.logging.logger_config import setup_logger
from backend.src.infrastructure.persistence.mysql_connector import MySQLConnector
from backend.src.infrastructure.scheduler.token_cleanup_scheduler import TokenCleanupScheduler
from backend.src.presentation.api.middleware.auth_middleware import JWTAuthMiddleware
from backend.src.presentation.api.middleware.request_id_middleware import request_id_middleware
from backend.src.presentation.api.routers import associator_router, clickup_router, repo_router, member_router, \
    deployment_router, auth_router

logger = logging.getLogger(__name__)



@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup and shutdown events.

    Args:
        app (FastAPI): The FastAPI application instance.

    Yields:
        None
    """
    # ── Startup ──
    logger.info("Application starting up.")

    db = MySQLConnector()
    db.create_db_if_not_exists()

    app.state.db = MySQLConnector()

    scheduler = TokenCleanupScheduler(db=app.state.db)
    scheduler.start()
    app.state.scheduler = scheduler

    yield

    # ── Shutdown ──
    logger.info("Application shutting down.")
    app.state.scheduler.stop()

def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        FastAPI: Configured FastAPI instance.
    """
    
    setup_logger() 

    app = FastAPI(
        title="ClickUp Integration API",
        description="Manage repositories, members, ClickUp spaces and deployments.",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.middleware("http")(request_id_middleware)

    app.add_exception_handler(AppException, FastAPIExceptionHandler.handle_app_exception)
    app.add_exception_handler(RequestValidationError, FastAPIExceptionHandler.handle_validation_exception)
    app.add_exception_handler(Exception, FastAPIExceptionHandler.handle_generic_exception)

    # Auth Middleware
    app.add_middleware(JWTAuthMiddleware)

    # Routers
    app.include_router(auth_router.router, prefix="/auth", tags=["auth"])
    app.include_router(clickup_router.router, prefix="/clickup", tags=["ClickUp"])
    app.include_router(associator_router.router, prefix="/associate", tags=["Associator"])
    app.include_router(repo_router.router, prefix="/repo", tags=["Repo"])
    app.include_router(member_router.router, prefix="/member", tags=["Member"])
    app.include_router(deployment_router.router, prefix="/deployment", tags=["Deployment"])
    return app


app = create_app()