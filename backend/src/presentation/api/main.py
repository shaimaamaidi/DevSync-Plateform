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
from backend.src.infrastructure.di.backlog_generation_container import BacklogGenerationContainer
from backend.src.infrastructure.di.clickup_container import ClickUpContainer
from backend.src.infrastructure.di.task_generation_container import TaskGenerationContainer
from backend.src.infrastructure.di.task_status_container import TaskStatusContainer
from backend.src.infrastructure.di.deployment_container import DeploymentContainer
from backend.src.infrastructure.handlers.exception_handler import FastAPIExceptionHandler
from backend.src.infrastructure.logging.logger_config import setup_logger
from backend.src.infrastructure.persistence.mysql_connector import MySQLConnector
from backend.src.infrastructure.scheduler.token_cleanup_scheduler import TokenCleanupScheduler
from backend.src.presentation.api.middleware.auth_middleware import JWTAuthMiddleware
from backend.src.presentation.api.middleware.request_id_middleware import request_id_middleware
from backend.src.presentation.api.routers import (
    associator_router, clickup_router, repo_router, member_router,
    deployment_router, auth_router, backlog_router, health_router,
    verification_tasks_from_summary_router, verification_tasks_from_backlog_router,
    generation_tasks_from_summary_router, summary_tasks_save_router,
    backlog_tasks_save_router, clickup_structure_metadata_router,
    clickup_structure_management_router, clickup_task_management_router,
    clickup_space_task_reader_router, generation_tasks_from_backlog_router,
    task_status_check_router
)


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle events (startup and shutdown).

    Startup sequence:
        1. Initialize logging and application context
        2. Create MySQL database connector
        3. Start token cleanup scheduler
        4. Initialize BacklogGenerationContainer (agents, tools, orchestrator)
        5. Initialize ClickUpContainer (ClickUp infrastructure + use cases)
        6. Initialize TaskGenerationContainer (task generation + verification agents)
        7. Initialize TaskStatusContainer (task status agents + use cases)
        8. Initialize DeploymentContainer (GitHub deployment adapter)
        9. Attach all containers to app.state

    Shutdown sequence:
        1. Stop background scheduler
        2. Cleanup BacklogGenerationContainer (web search agent, orchestrator)
        3. Close database connector

    Args:
        app (FastAPI): The FastAPI application instance.

    Yields:
        None: Control is returned to FastAPI during application runtime.

    Raises:
        Exception: If any startup component fails to initialize.
    """
    # ── Startup ──
    logger.info("Application starting up.")
    try:
        # ── Database ──
        app.state.db = MySQLConnector()

        # ── Scheduler ──
        scheduler = TokenCleanupScheduler(db=app.state.db)
        scheduler.start()
        app.state.scheduler = scheduler

        # ── BacklogGenerationContainer ──
        backlog_generation_container = BacklogGenerationContainer()
        await backlog_generation_container.initialize_web_search_tool()
        await backlog_generation_container.initialize_backlog_workflow_orchestrator()
        app.state.backlog_generation_container = backlog_generation_container

        # ── ClickUpContainer ──
        app.state.clickup_container = ClickUpContainer()

        # ── TaskGenerationContainer ──
        app.state.task_generation_container = TaskGenerationContainer()

        # ── TaskStatusContainer ──
        app.state.task_status_container = TaskStatusContainer()

        # ── DeploymentContainer ──
        app.state.deployment_container = DeploymentContainer()

        logger.info("Application started successfully.")

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
        await app.state.backlog_generation_container.cleanup()
        logger.info("Backlog generation container cleaned up.")
    except Exception:
        logger.warning("Failed to cleanup backlog generation container during shutdown.")

    try:
        app.state.db.close()
        logger.info("Database connector closed.")
    except Exception:
        logger.warning("Failed to close database connector during shutdown.")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application instance.

    Returns:
        FastAPI: Fully configured FastAPI application ready to serve requests.
    """
    setup_logger()

    app = FastAPI(
        title="AI Backlog Generation & ClickUp Integration API",
        description="REST API that orchestrates an AI-driven backlog generation workflow. It transforms product descriptions into structured epics, user stories, and tasks using market intelligence, then integrates the results with ClickUp for workspace, task, and team management automation.",
        version="1.0.0",
        lifespan=lifespan,
    )

    # ── Middleware ──
    app.add_middleware(JWTAuthMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.middleware("http")(request_id_middleware)

    # ── Exception Handlers ──
    app.add_exception_handler(AppException, FastAPIExceptionHandler.handle_app_exception)
    app.add_exception_handler(RequestValidationError, FastAPIExceptionHandler.handle_validation_exception)
    app.add_exception_handler(Exception, FastAPIExceptionHandler.handle_generic_exception)

    # ── Routers ──
    app.include_router(health_router.router, prefix="/health", tags=["health"])
    app.include_router(auth_router.router, prefix="/auth", tags=["auth"])
    app.include_router(clickup_router.router, prefix="/clickup", tags=["ClickUp"])
    app.include_router(associator_router.router, prefix="/associate", tags=["Associator"])
    app.include_router(repo_router.router, prefix="/repo", tags=["Repo"])
    app.include_router(member_router.router, prefix="/member", tags=["Member"])
    app.include_router(deployment_router.router, prefix="/deployment", tags=["Deployment"])
    app.include_router(backlog_router.router, prefix="/backlog", tags=["Backlog"])
    app.include_router(
        verification_tasks_from_summary_router.router,
        prefix="/clickup/tasks",
        tags=["ClickUp - Tasks"],
    )
    app.include_router(
        verification_tasks_from_backlog_router.router,
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
        summary_tasks_save_router.router,
        prefix="/clickup/tasks",
        tags=["ClickUp - Tasks"],
    )
    app.include_router(
        backlog_tasks_save_router.router,
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
    app.include_router(
        task_status_check_router.router,
        prefix="/task-status",
        tags=["Task Status Check"],
    )

    return app


app = create_app()