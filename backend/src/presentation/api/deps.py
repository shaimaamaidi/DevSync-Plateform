"""
FastAPI dependency providers.

This module defines dependency injection providers used by FastAPI routes.
It is responsible for building request-scoped infrastructure objects such as
the DI container and exposing application use cases initialized at startup.

Functions:
    get_container: Provides a request-scoped dependency injection container.
    get_backlog_use_case: Provides the backlog generation use case instance.
    get_verify_task_use_case: Provides the task verification use case instance.
    get_generate_task_from_summary_use_case: Provides the task generation from summary use case instance.
    get_save_task_use_case: Builds and provides the save task use case per request.
    get_clickup_structure_metadata_use_case: Provide the clickup structure metadata use case instance.
    get_clickup_structure_creation_use_case:
        Builds and provides the ClickUp workspace structure creation use case per request.
        This use case is responsible for creating ClickUp spaces, folders, lists, and statuses
        using request-scoped repository data combined with singleton infrastructure.
"""

import logging
from typing import Generator

from fastapi import Depends, Request

from backend.src.application.use_cases.clickup_space_task_reader_use_case import ClickUpSpaceTaskReaderUseCase
from backend.src.application.use_cases.clickup_structure_management_use_case import ClickUpStructureManagementUseCase
from backend.src.application.use_cases.clickup_structure_metadata_use_case import ClickUpStructureMetadataUseCase
from backend.src.application.use_cases.clickup_task_management_use_case import ClickUpTaskManagementUseCase
from backend.src.application.use_cases.generate_backlog_use_case import GenerateBacklogUseCase
from backend.src.application.use_cases.generate_tasks_from_backlog_use_case import GenerateTasksFromBacklogUseCase
from backend.src.application.use_cases.generate_tasks_from_summary_use_case import GenerateTasksFromSummaryUseCase
from backend.src.application.use_cases.save_task_in_clickup_use_case import SaveTaskInClickUpUseCase
from backend.src.application.use_cases.verify_tasks_use_case import VerifyTasksUseCase
from backend.src.domain.exceptions.base.app_exception import AppException
from backend.src.domain.exceptions.system.service_unavailable_exception import ServiceUnavailableException
from backend.src.infrastructure.di.container import Container


logger = logging.getLogger(__name__)


# Request-scoped container
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
        request (Request): The incoming FastAPI request object.

    Yields:
        Container: A request-scoped dependency injection container configured with a database
            session and application services.

    Raises:
        AppException: Re-raised if a known application-level exception occurs during container
            initialization or usage.

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
        logger.exception("Error while creating container for request: %s.", str(e))
        raise
    finally:
        session.close()
        logger.info("Closed DI container for request: %s", request.url.path)


# Singleton use cases (initialized at startup)
def get_backlog_use_case(request: Request) -> GenerateBacklogUseCase:
    """
    Retrieve the backlog generation use case instance.

    This dependency provides access to a singleton instance of the backlog
    generation use case, initialized at application startup. It is not
    request-scoped and does not create new instances per call.

    Args:
        request (Request): The incoming FastAPI request object.

    Returns:
        GenerateBacklogUseCase: The initialized backlog generation use case responsible for
            orchestrating the full backlog generation workflow.

    Raises:
        ServiceUnavailableException: If the use case is not initialized in the application state,
            or if an unexpected runtime error occurs while resolving the dependency.

    Notes:
        - Stored in app.state.workflow_container.
        - Initialized once at startup to improve performance.
        - Must NOT be modified per request.
    """
    try:
        use_case = request.app.state.workflow_container.generate_backlog_use_case

        if use_case is None:
            raise ServiceUnavailableException("Backlog use case is not initialized.")

        return use_case

    except ServiceUnavailableException:
        raise

    except Exception as e:
        logger.exception("Failed to retrieve backlog use case: %s", str(e))
        raise ServiceUnavailableException("Backlog service is unavailable.") from e

def get_generate_task_from_summary_use_case(request: Request) -> GenerateTasksFromSummaryUseCase:
    """
    Retrieve the task generation from summary use case instance.

    Singleton initialized at application startup. Generates structured ClickUp
    tasks from a plain-text summary using an LLM-based agent.

    Args:
        request (Request): The incoming FastAPI request object.

    Returns:
        GenerateTasksFromSummaryUseCase: The initialized task generation from summary use case.

    Raises:
        ServiceUnavailableException: If the use case is not initialized in the application state,
            or if an unexpected runtime error occurs while resolving the dependency.
    """
    try:
        use_case = request.app.state.workflow_container.clickup_task_generator_from_summary_use_case

        if use_case is None:
            raise ServiceUnavailableException("Task generation from summary use case is not initialized.")

        return use_case

    except ServiceUnavailableException:
        raise

    except Exception as e:
        logger.exception("Failed to retrieve task generation from summary use case: %s", str(e))
        raise ServiceUnavailableException("Task generation from summary service is unavailable.") from e

def get_generate_task_from_backlog_use_case(request: Request) -> GenerateTasksFromBacklogUseCase:
    """
    Retrieve the task generation from backlog use case instance.

    Singleton initialized at application startup. Generates structured ClickUp
    tasks from a sprint backlog using an LLM-based agent.

    Args:
        request (Request): The incoming FastAPI request object.

    Returns:
        GenerateTasksFromBacklogUseCase: The initialized task generation from backlog use case.

    Raises:
        ServiceUnavailableException: If the use case is not initialized in the application state,
            or if an unexpected runtime error occurs while resolving the dependency.
    """
    try:
        use_case = request.app.state.workflow_container.clickup_task_generator_from_backlog_use_case

        if use_case is None:
            raise ServiceUnavailableException("Task generation from backlog use case is not initialized.")

        return use_case

    except ServiceUnavailableException:
        raise

    except Exception as e:
        logger.exception("Failed to retrieve task generation from backlog use case: %s", str(e))
        raise ServiceUnavailableException("Task generation from backlog service is unavailable.") from e

def get_clickup_task_creation_use_case(request: Request) -> ClickUpTaskManagementUseCase:
    """
    Retrieve the ClickUp task creation use case instance.

    This dependency provides access to a singleton instance of the task
    creation use case, initialized at application startup. It handles
    task creation, update, and deletion operations.

    Args:
        request (Request): The incoming FastAPI request object.

    Returns:
        ClickUpTaskManagementUseCase: The initialized task creation use case.

    Raises:
        ServiceUnavailableException: If the use case is not initialized in the application state,
            or if an unexpected runtime error occurs while resolving the dependency.
    """
    try:
        use_case = request.app.state.workflow_container.clickup_task_creation_use_case

        if use_case is None:
            raise ServiceUnavailableException("ClickUp task creation use case is not initialized.")

        return use_case

    except ServiceUnavailableException:
        raise

    except Exception as e:
        logger.exception("Failed to retrieve ClickUp task creation use case: %s", str(e))
        raise ServiceUnavailableException("ClickUp task creation service is unavailable.") from e

def get_clickup_space_task_reader_use_case(request: Request) -> ClickUpSpaceTaskReaderUseCase:
    """
    Retrieve the ClickUp space task reader use case instance.

    Provides access to a singleton instance initialized at application
    startup for read-only access to ClickUp space task structures.

    Args:
        request (Request): The incoming FastAPI request object.

    Returns:
        ClickUpSpaceTaskReaderUseCase: The initialized use case.

    Raises:
        ServiceUnavailableException: If the use case is not initialized in the application state,
            or if an unexpected runtime error occurs while resolving the dependency.
    """
    try:
        use_case = request.app.state.workflow_container.clickup_space_task_reader_use_case

        if use_case is None:
            raise ServiceUnavailableException("ClickUp space task reader use case is not initialized.")

        return use_case

    except ServiceUnavailableException:
        raise

    except Exception as e:
        logger.exception("Failed to retrieve ClickUp space task reader use case: %s", str(e))
        raise ServiceUnavailableException("ClickUp space task reader service is unavailable.") from e

def get_clickup_structure_metadata_use_case(request: Request) -> ClickUpStructureMetadataUseCase:
    """
    Retrieve the ClickUp structure metadata use case instance.

    Singleton initialized at application startup. Provides read-only access
    to ClickUp workspace structural data (folders, lists).

    Args:
        request (Request): The incoming FastAPI request object.

    Returns:
        ClickUpStructureMetadataUseCase: The initialized metadata use case.

    Raises:
        ServiceUnavailableException: If the use case is not initialized in the application state,
            or if an unexpected runtime error occurs while resolving the dependency.
    """
    try:
        use_case = request.app.state.workflow_container.clickup_structure_metadata_use_case

        if use_case is None:
            raise ServiceUnavailableException("ClickUp structure metadata use case is not initialized.")

        return use_case

    except ServiceUnavailableException:
        raise

    except Exception as e:
        logger.exception("Failed to retrieve ClickUp structure metadata use case: %s", str(e))
        raise ServiceUnavailableException("ClickUp structure metadata service is unavailable.") from e

# Request-scoped use case (requires member_repo)
def get_save_task_use_case(
    request: Request,
    container: Container = Depends(get_container),
) -> SaveTaskInClickUpUseCase:
    """
    Build and provide the save task use case for the current request.

    Unlike the other use cases, SaveTaskInClickUpUseCase requires member_repo
    which is request-scoped (bound to a SQLAlchemy session). It is therefore
    constructed fresh per request by combining:
        - Singleton ClickUp infrastructure from WorkflowContainer (app.state)
        - Request-scoped member_repo from the session-bound Container

    Args:
        request (Request): The incoming FastAPI request object.
        container (Container): The request-scoped DI container providing member_repo.

    Returns:
        SaveTaskInClickUpUseCase: A fully initialized save task use case for this request.

    Raises:
        ServiceUnavailableException: If the ClickUp infrastructure is not initialized in the
            application state, or if an unexpected error occurs while building the use case.
    """
    try:
        return request.app.state.workflow_container.create_save_task_use_case(
            member_repo=container.member_repo
        )
    except ServiceUnavailableException:
        raise
    except Exception as e:
        logger.exception("Failed to build save task use case: %s", str(e))
        raise ServiceUnavailableException("Save task service is unavailable.") from e

# Request-scoped use case (requires member_repo)
def get_verify_tasks_use_case(
    request: Request,
    container: Container = Depends(get_container),
) -> VerifyTasksUseCase:
    """
    Build and provide the verify tasks use case for the current request.

    Unlike the other use cases, VerifyTasksUseCase requires member_repo
    which is request-scoped (bound to a SQLAlchemy session). It is therefore
    constructed fresh per request by combining:
        - Singleton ClickUp infrastructure from WorkflowContainer (app.state)
        - Request-scoped member_repo from the session-bound Container

    Args:
        request (Request): The incoming FastAPI request object.
        container (Container): The request-scoped DI container providing member_repo.

    Returns:
        VerifyTasksUseCase: A fully initialized verify tasks use case for this request.

    Raises:
        ServiceUnavailableException: If the ClickUp infrastructure is not initialized in
            the application state, or if an unexpected error occurs while building the use case.
    """
    try:
        return request.app.state.workflow_container.create_tasks_verification_use_case(
            member_repo=container.member_repo
        )
    except ServiceUnavailableException:
        raise
    except Exception as e:
        logger.exception("Failed to build save task use case: %s", str(e))
        raise ServiceUnavailableException("Verify task service is unavailable.") from e

# Request-scoped use case (requires clickup_repo)
def get_clickup_structure_creation_use_case(
    request: Request,
    container: Container = Depends(get_container),
) -> ClickUpStructureManagementUseCase:
    """
    Build and provide the ClickUp structure creation use case for the current request.

    This dependency constructs a request-scoped use case responsible for creating
    ClickUp workspace structures such as:
        - Spaces
        - Folders
        - Lists
        - Statuses

    It combines:
        - Singleton ClickUp infrastructure stored in application state
        - Request-scoped repository access (clickup_repo) from DI container

    This ensures that workspace creation operations are properly isolated per request
    while still reusing shared infrastructure components.

    Args:
        request (Request): The incoming FastAPI request object.
        container (Container): The request-scoped dependency injection container providing
            repositories.

    Returns:
        ClickUpStructureManagementUseCase: A fully initialized use case responsible for creating
            ClickUp workspace structure.

    Raises:
        ServiceUnavailableException: If ClickUp infrastructure is not initialized in application state,
            or if an unexpected error occurs during use case construction.

    Notes:
        - This use case is request-scoped due to repository dependency.
        - ClickUp writer infrastructure is shared (singleton via workflow container).
        - Ensures separation between structure creation logic and persistence layer.
    """
    try:
        return request.app.state.workflow_container.create_clickup_structure_creation_use_case(
            clickup_repo=container.clickup_repo,
            member_repo=container.member_repo,
        )
    except ServiceUnavailableException:
        raise
    except Exception as e:
        logger.exception("Failed to build clickup structure creation use case: %s", str(e))
        raise ServiceUnavailableException("Creation clickup structure service is unavailable.") from e
