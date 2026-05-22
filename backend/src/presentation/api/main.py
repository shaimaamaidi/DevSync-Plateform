"""
FastAPI application factory.

This module defines the FastAPI application factory responsible for building
and configuring the application instance. It handles startup and shutdown
lifecycle events, middleware registration, exception handling, and router setup.

Responsibilities:
    - Initialize infrastructure (database, scheduler, DI containers)
    - Configure application lifespan (startup/shutdown hooks)
    - Register middleware (auth, CORS, request tracking)
    - Register global exception handlers
    - Mount API routers

Functions:
    lifespan: Async context manager handling startup and shutdown events.
    create_app: Creates and configures the FastAPI application instance.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from backend.src.domain.exceptions.base.app_exception import AppException
from backend.src.infrastructure.di.WorkflowContainer import WorkflowContainer
from backend.src.infrastructure.handlers.exception_handler import FastAPIExceptionHandler
from backend.src.infrastructure.logging.logger_config import setup_logger
from backend.src.infrastructure.persistence.mysql_connector import MySQLConnector
from backend.src.infrastructure.scheduler.token_cleanup_scheduler import TokenCleanupScheduler
from backend.src.presentation.api.middleware.auth_middleware import JWTAuthMiddleware
from backend.src.presentation.api.middleware.request_id_middleware import request_id_middleware
from backend.src.presentation.api.routers import (
    associator_router, clickup_router, repo_router, member_router,
    deployment_router, auth_router, backlog_router, health_router, verification_tasks_router,
    generation_tasks_from_summary_router, clickup_task_save_router,
    clickup_structure_metadata_router, clickup_structure_management_router, clickup_task_management_router,
    clickup_space_task_reader_router, generation_tasks_from_backlog_router
)


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle events (startup and shutdown).

    This function is executed by FastAPI when the application starts and stops.
    It is responsible for initializing infrastructure components such as:
    - Database connection manager
    - Background schedulers
    - Backlog workflow container and tools

    Startup sequence:
        1. Initialize logging and application context
        2. Create MySQL database connector
        3. Start token cleanup scheduler
        4. Initialize backlog workflow container and tools
        5. Attach components to app.state

    Shutdown sequence:
        1. Stop background scheduler
        2. Release resources and gracefully shutdown services

    Args:
        app (FastAPI):
            The FastAPI application instance.

    Yields:
        None:
            Control is returned to FastAPI during application runtime.

    Raises:
        Exception: If any startup component fails to initialize (database connector, scheduler,
            web search tool, or backlog workflow orchestrator), or if an unexpected runtime
            error occurs during application startup or shutdown.
    """
    # ── Startup ──
    logger.info("Application starting up.")
    try:
        app.state.db = MySQLConnector()

        # ── Scheduler ──
        scheduler = TokenCleanupScheduler(db=app.state.db)
        scheduler.start()
        app.state.scheduler = scheduler

        # ── Backlog Workflow ──
        workflow_container = WorkflowContainer()
        await workflow_container.initialize_web_search_tool()
        await workflow_container.initialize_backlog_workflow_orchestrator()
        app.state.workflow_container = workflow_container
    except Exception as e:
        logger.exception("Application startup failed: %s", str(e))
        raise

    yield

    # ── Shutdown ──
    logger.info("Application shutting down.")

    try:
        app.state.scheduler.stop()
    except Exception:
        logger.warning("Failed to stop scheduler during shutdown.")

    try:
        await app.state.workflow_container.cleanup()
        logger.info("Backlog container cleaned up.")
    except Exception:
        logger.warning("Failed to cleanup backlog container during shutdown.")

    try:
        app.state.db.close()
        logger.info("Database connector closed.")
    except Exception:
        logger.warning("Failed to close database connector during shutdown.")

def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application instance.

    This factory function builds the complete FastAPI application by:
    - Initializing logging configuration
    - Creating the FastAPI instance
    - Registering middleware (authentication, CORS, request ID tracking)
    - Registering global exception handlers
    - Mounting all API routers with prefixes and tags

    Returns:
        FastAPI:
            Fully configured FastAPI application ready to serve requests.

    Notes:
        - This function is the single entry point for application creation.
        - It ensures consistent configuration across environments.
    """
    setup_logger()

    app = FastAPI(
        title="AI Backlog Generation & ClickUp Integration API",
        description="REST API that orchestrates an AI-driven backlog generation workflow. It transforms product descriptions into structured epics, user stories, and tasks using market intelligence, then integrates the results with ClickUp for workspace, task, and team management automation.",
        version="1.0.0",
        lifespan=lifespan,
    )

    # Auth Middleware
    app.add_middleware(JWTAuthMiddleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.middleware("http")(request_id_middleware)

    app.add_exception_handler(AppException, FastAPIExceptionHandler.handle_app_exception)
    app.add_exception_handler(RequestValidationError, FastAPIExceptionHandler.handle_validation_exception)
    app.add_exception_handler(Exception, FastAPIExceptionHandler.handle_generic_exception)

    # Routers
    app.include_router(health_router.router, prefix="/health", tags=["health"])
    app.include_router(auth_router.router, prefix="/auth", tags=["auth"])
    app.include_router(clickup_router.router, prefix="/clickup", tags=["ClickUp"])
    app.include_router(associator_router.router, prefix="/associate", tags=["Associator"])
    app.include_router(repo_router.router, prefix="/repo", tags=["Repo"])
    app.include_router(member_router.router, prefix="/member", tags=["Member"])
    app.include_router(deployment_router.router, prefix="/deployment", tags=["Deployment"])
    app.include_router(backlog_router.router, prefix="/backlog", tags=["Backlog"])
    app.include_router(
        verification_tasks_router.router,
        prefix="/clickup/tasks",
        tags=["ClickUp - Tasks"],
    )
    app.include_router(
        generation_tasks_from_summary_router.router,
        prefix="/clickup/tasks",
        tags=["ClickUp - Tasks"],
    )
    app.include_router(
        generation_tasks_from_backlog_router.router,
        prefix="/clickup/tasks",
        tags=["ClickUp - Tasks"],
    )
    app.include_router(
        clickup_task_save_router.router,
        prefix="/clickup/tasks",
        tags=["ClickUp - Tasks"],
    )
    app.include_router(
        clickup_structure_metadata_router.router,
        prefix="/clickup/structure",
        tags=["ClickUp Structure Metadata"],
    )
    app.include_router(
        clickup_structure_management_router.router,
        prefix="/clickup/structure",
        tags=["ClickUp Structure Creation"],
    )
    app.include_router(
        clickup_task_management_router.router,
        prefix="/clickup/tasks/manage",
        tags=["ClickUp - Tasks"],
    )
    app.include_router(
        clickup_space_task_reader_router.router,
        prefix="/clickup/tasks/spaces",
        tags=["ClickUp - Tasks"],
    )

    return app


app = create_app()