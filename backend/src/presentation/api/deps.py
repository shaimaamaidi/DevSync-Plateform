"""
FastAPI dependency providers.

This module defines dependency injection providers used by FastAPI routes.
It is responsible for building request-scoped infrastructure objects such as
the DI container and exposing application use cases initialized at startup.

Functions:
    get_persistence_container: Provides a request-scoped PersistenceContainer.

    # DeploymentContainer
    get_deployment_use_case: Provide the deployments fetching use case instance.

    # BacklogGenerationContainer
    get_generate_backlog_use_case: Provides the backlog generation use case instance.

    # TaskGenerationContainer
    get_generate_task_from_summary_use_case: Provides the task generation from summary use case instance.
    get_generate_task_from_backlog_use_case: Provides the task generation from backlog use case instance.
    get_save_summary_tasks_use_case: Builds the saving summary tasks use case per request.
    get_save_backlog_tasks_use_case: Builds the saving backlog tasks use case per request.
    get_verify_tasks_from_summary_use_case: Builds the verification tasks from summary use case per request.
    get_verify_tasks_from_backlog_use_case: Builds the verification  tasks from backlog use case per request.

    # ClickUpContainer
    get_create_clickup_task_use_case: Provides the ClickUp task management use case instance.
    get_read_clickup_space_task_use_case: Provides the ClickUp space task reader use case instance.
    get_clickup_structure_metadata_use_case: Provides the ClickUp structure metadata use case instance.
    get_create_clickup_structure_use_case: Builds the ClickUp structure creation use case per request.

    # TaskStatusContainer
    get_search_task_use_case: Provides the task search use case instance.
    get_synthesize_task_status_use_case: Provides the task status synthesis use case instance.

    # ProjectStatusContainer
    get_check_project_status_use_case: Provide the project status checking use case instance.

    # WeeklyProjectSummarizationContainer
    get_summarize_weekly_project_use_case: Provide the weekly project summarization use case instance.
    
    # CommitTaskMappingContainer
    get_map_commit_task_use_case: Provide the commit to task mapping use case instance.
"""

import logging
from typing import Generator

from fastapi import Depends, Request

from backend.src.application.use_cases.check_project_status_use_case import CheckProjectStatusUseCase
from backend.src.application.use_cases.read_clickup_space_task_use_case import ReadClickUpSpaceTaskUseCase
from backend.src.application.use_cases.manage_clickup_structure_use_case import ManageClickUpStructureUseCase
from backend.src.application.use_cases.clickup_structure_metadata_use_case import ClickUpStructureMetadataUseCase
from backend.src.application.use_cases.manage_clickup_task_use_case import ManageClickUpTaskUseCase
from backend.src.application.use_cases.deployment_use_case import DeploymentUseCase
from backend.src.application.use_cases.generate_backlog_use_case import GenerateBacklogUseCase
from backend.src.application.use_cases.generate_tasks_from_backlog_use_case import GenerateTasksFromBacklogUseCase
from backend.src.application.use_cases.generate_tasks_from_summary_use_case import GenerateTasksFromSummaryUseCase
from backend.src.application.use_cases.map_commit_task_use_case import MapCommitTaskUseCase
from backend.src.application.use_cases.save_backlog_tasks_use_case import SaveBacklogTasksInClickUpUseCase
from backend.src.application.use_cases.save_summary_tasks_use_case import SaveSummaryTasksInClickUpUseCase
from backend.src.application.use_cases.summarize_weekly_project_use_case import SummarizeWeeklyProjectUseCase
from backend.src.application.use_cases.task_status_check.search_task_use_case import SearchTaskUseCase
from backend.src.application.use_cases.task_status_check.synthesize_task_status_use_case import \
    SynthesizeTaskStatusUseCase
from backend.src.application.use_cases.verify_tasks_from_backlog_use_case import VerifyTasksFromBacklogUseCase
from backend.src.application.use_cases.verify_tasks_from_summary_use_case import VerifyTasksFromSummaryUseCase
from backend.src.domain.exceptions.base.app_exception import AppException
from backend.src.domain.exceptions.system.service_unavailable_exception import ServiceUnavailableException
from backend.src.infrastructure.di.persistence_container import PersistenceContainer


logger = logging.getLogger(__name__)


# Request-scoped container

def get_persistence_container(request: Request) -> Generator[PersistenceContainer, None, None]:
    """
    Provide a request-scoped PersistenceContainer.

    Lifecycle:
        - Retrieve DB session from application state
        - Initialize PersistenceContainer with session
        - Yield container to FastAPI route
        - Close session after request completion

    Args:
        request (Request): The incoming FastAPI request object.

    Yields:
        PersistenceContainer: A request-scoped container configured with a database session.

    Raises:
        AppException: Re-raised if a known application-level exception occurs.
    """
    logger.info("Creating DI persistence container for request: %s", request.url.path)

    session = request.app.state.db.get_session()
    try:
        yield PersistenceContainer(session)
    except AppException:
        raise
    except Exception as e:
        logger.exception("Error while creating persistence container for request: %s.", str(e))
        raise
    finally:
        session.close()
        logger.info("Closed DI container for request: %s", request.url.path)

# Singleton use cases — BacklogGenerationContainer

def get_generate_backlog_use_case(request: Request) -> GenerateBacklogUseCase:
    """
    Retrieve the backlog generation use case from BacklogGenerationContainer.

    Args:
        request (Request): The incoming FastAPI request object.

    Returns:
        GenerateBacklogUseCase: The initialized backlog generation use case.

    Raises:
        ServiceUnavailableException: If the use case is not initialized.
    """
    try:
        use_case = request.app.state.backlog_generation_container.generate_backlog_use_case

        if use_case is None:
            raise ServiceUnavailableException("Backlog use case is not initialized.")

        return use_case

    except ServiceUnavailableException:
        raise
    except Exception as e:
        logger.exception("Failed to retrieve backlog use case: %s", str(e))
        raise ServiceUnavailableException("Backlog service is unavailable.") from e

# Singleton use cases — TaskGenerationContainer

def get_generate_task_from_summary_use_case(request: Request) -> GenerateTasksFromSummaryUseCase:
    """
    Retrieve the task generation from summary use case from TaskGenerationContainer.

    Args:
        request (Request): The incoming FastAPI request object.

    Returns:
        GenerateTasksFromSummaryUseCase: The initialized use case.

    Raises:
        ServiceUnavailableException: If the use case is not initialized.
    """
    try:
        use_case = request.app.state.task_generation_container.clickup_task_generator_from_summary_use_case

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
    Retrieve the task generation from backlog use case from TaskGenerationContainer.

    Args:
        request (Request): The incoming FastAPI request object.

    Returns:
        GenerateTasksFromBacklogUseCase: The initialized use case.

    Raises:
        ServiceUnavailableException: If the use case is not initialized.
    """
    try:
        use_case = request.app.state.task_generation_container.clickup_task_generator_from_backlog_use_case

        if use_case is None:
            raise ServiceUnavailableException("Task generation from backlog use case is not initialized.")

        return use_case

    except ServiceUnavailableException:
        raise
    except Exception as e:
        logger.exception("Failed to retrieve task generation from backlog use case: %s", str(e))
        raise ServiceUnavailableException("Task generation from backlog service is unavailable.") from e

# Singleton use cases — ClickUpContainer

def get_create_clickup_task_use_case(request: Request) -> ManageClickUpTaskUseCase:
    """
    Retrieve the ClickUp task management use case from ClickUpContainer.

    Args:
        request (Request): The incoming FastAPI request object.

    Returns:
        ManageClickUpTaskUseCase: The initialized use case.

    Raises:
        ServiceUnavailableException: If the use case is not initialized.
    """
    try:
        use_case = request.app.state.clickup_container.clickup_task_creation_use_case

        if use_case is None:
            raise ServiceUnavailableException("ClickUp task creation use case is not initialized.")

        return use_case

    except ServiceUnavailableException:
        raise
    except Exception as e:
        logger.exception("Failed to retrieve ClickUp task creation use case: %s", str(e))
        raise ServiceUnavailableException("ClickUp task creation service is unavailable.") from e

def get_read_clickup_space_task_use_case(request: Request) -> ReadClickUpSpaceTaskUseCase:
    """
    Retrieve the ClickUp space task reader use case from ClickUpContainer.

    Args:
        request (Request): The incoming FastAPI request object.

    Returns:
        ReadClickUpSpaceTaskUseCase: The initialized use case.

    Raises:
        ServiceUnavailableException: If the use case is not initialized.
    """
    try:
        use_case = request.app.state.clickup_container.clickup_space_task_reader_use_case

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
    Retrieve the ClickUp structure metadata use case from ClickUpContainer.

    Args:
        request (Request): The incoming FastAPI request object.

    Returns:
        ClickUpStructureMetadataUseCase: The initialized use case.

    Raises:
        ServiceUnavailableException: If the use case is not initialized.
    """
    try:
        use_case = request.app.state.clickup_container.clickup_structure_metadata_use_case

        if use_case is None:
            raise ServiceUnavailableException("ClickUp structure metadata use case is not initialized.")

        return use_case

    except ServiceUnavailableException:
        raise
    except Exception as e:
        logger.exception("Failed to retrieve ClickUp structure metadata use case: %s", str(e))
        raise ServiceUnavailableException("ClickUp structure metadata service is unavailable.") from e

# Request-scoped use cases — DeploymentContainer + PersistenceContainer

def get_deployment_use_case(
    request: Request,
    container: PersistenceContainer = Depends(get_persistence_container),
) -> DeploymentUseCase:
    """
    Build the save summary tasks use case for the current request.

    Combines singleton TaskGenerationContainer infrastructure with
    request-scoped member_repo from PersistenceContainer.

    Args:
        request (Request): The incoming FastAPI request object.
        container (PersistenceContainer): The request-scoped DI container.

    Returns:
        SaveSummaryTasksInClickUpUseCase: A fully initialized use case for this request.

    Raises:
        ServiceUnavailableException: If ClickUp infrastructure is not initialized.
    """
    try:
        use_case = request.app.state.deployment_container.create_deployment_use_case(
            container.repo_repo
        )

        if use_case is None:
            raise ServiceUnavailableException("Backlog use case is not initialized.")

        return use_case

    except ServiceUnavailableException:
        raise
    except Exception as e:
        logger.exception("Failed to retrieve backlog use case: %s", str(e))
        raise ServiceUnavailableException("Backlog service is unavailable.") from e

# Request-scoped use cases — TaskGenerationContainer + PersistenceContainer

def get_save_summary_tasks_use_case(
    request: Request,
    container: PersistenceContainer = Depends(get_persistence_container),
) -> SaveSummaryTasksInClickUpUseCase:
    """
    Build the save summary tasks use case for the current request.

    Combines singleton TaskGenerationContainer infrastructure with
    request-scoped member_repo from PersistenceContainer.

    Args:
        request (Request): The incoming FastAPI request object.
        container (PersistenceContainer): The request-scoped DI container.

    Returns:
        SaveSummaryTasksInClickUpUseCase: A fully initialized use case for this request.

    Raises:
        ServiceUnavailableException: If ClickUp infrastructure is not initialized.
    """
    try:
        return request.app.state.task_generation_container.create_save_summary_tasks_use_case(
            member_repo=container.member_repo
        )
    except ServiceUnavailableException:
        raise
    except Exception as e:
        logger.exception("Failed to build save summary task use case: %s", str(e))
        raise ServiceUnavailableException("Save summary task service is unavailable.") from e

def get_save_backlog_tasks_use_case(
    request: Request,
    container: PersistenceContainer = Depends(get_persistence_container),
) -> SaveBacklogTasksInClickUpUseCase:
    """
    Build the save backlog tasks use case for the current request.

    Combines singleton TaskGenerationContainer infrastructure with
    request-scoped member_repo from PersistenceContainer.

    Args:
        request (Request): The incoming FastAPI request object.
        container (PersistenceContainer): The request-scoped DI container.

    Returns:
        SaveBacklogTasksInClickUpUseCase: A fully initialized use case for this request.

    Raises:
        ServiceUnavailableException: If ClickUp infrastructure is not initialized.
    """
    try:
        return request.app.state.task_generation_container.create_save_backlog_tasks_use_case(
            member_repo=container.member_repo
        )
    except ServiceUnavailableException:
        raise
    except Exception as e:
        logger.exception("Failed to build save backlog task use case: %s", str(e))
        raise ServiceUnavailableException("Save backlog task service is unavailable.") from e

def get_verify_tasks_from_summary_use_case(
    request: Request,
    container: PersistenceContainer = Depends(get_persistence_container),
) -> VerifyTasksFromSummaryUseCase:
    """
    Build the verify tasks from summary use case for the current request.

    Combines singleton TaskGenerationContainer infrastructure with
    request-scoped member_repo from PersistenceContainer.

    Args:
        request (Request): The incoming FastAPI request object.
        container (PersistenceContainer): The request-scoped DI container.

    Returns:
        VerifyTasksFromSummaryUseCase: A fully initialized use case for this request.

    Raises:
        ServiceUnavailableException: If ClickUp infrastructure is not initialized.
    """
    try:
        return request.app.state.task_generation_container.create_tasks_from_summary_verification_use_case(
            member_repo=container.member_repo
        )
    except ServiceUnavailableException:
        raise
    except Exception as e:
        logger.exception("Failed to build verify task from summary use case: %s", str(e))
        raise ServiceUnavailableException("Verify task from summary service is unavailable.") from e

def get_verify_tasks_from_backlog_use_case(
    request: Request,
    container: PersistenceContainer = Depends(get_persistence_container),
) -> VerifyTasksFromBacklogUseCase:
    """
    Build the verify tasks from backlog use case for the current request.

    Combines singleton TaskGenerationContainer infrastructure with
    request-scoped member_repo from PersistenceContainer.

    Args:
        request (Request): The incoming FastAPI request object.
        container (PersistenceContainer): The request-scoped DI container.

    Returns:
        VerifyTasksFromBacklogUseCase: A fully initialized use case for this request.

    Raises:
        ServiceUnavailableException: If ClickUp infrastructure is not initialized.
    """
    try:
        return request.app.state.task_generation_container.create_tasks_from_backlog_verification_use_case(
            member_repo=container.member_repo
        )
    except ServiceUnavailableException:
        raise
    except Exception as e:
        logger.exception("Failed to build verify task from backlog use case: %s", str(e))
        raise ServiceUnavailableException("Verify task from backlog service is unavailable.") from e

# Request-scoped use cases — ClickUpContainer + PersistenceContainer

def get_create_clickup_structure_use_case(
    request: Request,
    container: PersistenceContainer = Depends(get_persistence_container),
) -> ManageClickUpStructureUseCase:
    """
    Build the ClickUp structure creation use case for the current request.

    Combines singleton ClickUpContainer infrastructure with
    request-scoped clickup_repo and member_repo from PersistenceContainer.

    Args:
        request (Request): The incoming FastAPI request object.
        container (PersistenceContainer): The request-scoped DI container.

    Returns:
        ManageClickUpStructureUseCase: A fully initialized use case for this request.

    Raises:
        ServiceUnavailableException: If ClickUp infrastructure is not initialized.
    """
    try:
        return request.app.state.clickup_container.create_clickup_structure_creation_use_case(
            clickup_repo=container.clickup_repo,
            member_repo=container.member_repo,
        )
    except ServiceUnavailableException:
        raise
    except Exception as e:
        logger.exception("Failed to build ClickUp structure creation use case: %s", str(e))
        raise ServiceUnavailableException("ClickUp structure creation service is unavailable.") from e

# Singleton use cases — TaskStatusContainer

def get_search_task_use_case(request: Request) -> SearchTaskUseCase:
    """
    Retrieve the task search use case from TaskStatusContainer.

    Args:
        request (Request): The incoming FastAPI request object.

    Returns:
        SearchTaskUseCase: The initialized task search use case.

    Raises:
        ServiceUnavailableException: If the use case is not initialized.
    """
    try:
        use_case = request.app.state.task_status_container.task_search_use_case

        if use_case is None:
            raise ServiceUnavailableException("Task search use case is not initialized.")

        return use_case

    except ServiceUnavailableException:
        raise
    except Exception as e:
        logger.exception("Failed to retrieve task search use case: %s", str(e))
        raise ServiceUnavailableException("Task search service is unavailable.") from e

def get_synthesize_task_status_use_case(request: Request) -> SynthesizeTaskStatusUseCase:
    """
    Retrieve the task status synthesis use case from TaskStatusContainer.

    Args:
        request (Request): The incoming FastAPI request object.

    Returns:
        SynthesizeTaskStatusUseCase: The initialized task status synthesis use case.

    Raises:
        ServiceUnavailableException: If the use case is not initialized.
    """
    try:
        use_case = request.app.state.task_status_container.task_status_synthesize_use_case

        if use_case is None:
            raise ServiceUnavailableException("Task status synthesis use case is not initialized.")

        return use_case

    except ServiceUnavailableException:
        raise
    except Exception as e:
        logger.exception("Failed to retrieve task status synthesis use case: %s", str(e))
        raise ServiceUnavailableException("Task status synthesis service is unavailable.") from e

# Singleton use cases — ProjectStatusContainer

def get_check_project_status_use_case(request: Request) -> CheckProjectStatusUseCase:
    """
    Retrieve the project status checking use case from ProjectStatusContainer.

    Args:
        request (Request): The incoming FastAPI request object.

    Returns:
        CheckProjectStatusUseCase: The initialized project status checking use case.

    Raises:
        ServiceUnavailableException: If the use case is not initialized.
    """
    try:
        use_case = request.app.state.project_status_container.project_status_check_use_case

        if use_case is None:
            raise ServiceUnavailableException("Project status checking use case is not initialized.")

        return use_case

    except ServiceUnavailableException:
        raise
    except Exception as e:
        logger.exception("Failed to retrieve project status checking use case: %s", str(e))
        raise ServiceUnavailableException("Project status checking service is unavailable.") from e

# Singleton use cases — WeeklyProjectSummarizationContainer

def get_summarize_weekly_project_use_case(request: Request) -> SummarizeWeeklyProjectUseCase:
    """
    Retrieve the weekly project summarization use case from WeeklyProjectSummarizationContainer.

    Args:
        request (Request): The incoming FastAPI request object.

    Returns:
        CheckProjectStatusUseCase: The initialized weekly project summarization use case.

    Raises:
        ServiceUnavailableException: If the use case is not initialized.
    """
    try:
        use_case = request.app.state.weekly_project_summary_container.weekly_project_summarizer_use_case

        if use_case is None:
            raise ServiceUnavailableException("Weekly project summarizer use case is not initialized.")

        return use_case

    except ServiceUnavailableException:
        raise
    except Exception as e:
        logger.exception("Failed to retrieve weekly project summarizer use case: %s", str(e))
        raise ServiceUnavailableException("Weekly project summarizer service is unavailable.") from e

# Singleton use cases — CommitTaskMappingContainer

def get_map_commit_task_use_case(request: Request) -> MapCommitTaskUseCase:
    """
    Retrieve the commit task mapping use case from CommitTaskMappingContainer.

    Args:
        request (Request): The incoming FastAPI request object.

    Returns:
        CheckProjectStatusUseCase: The initialized commit task mapping use case.

    Raises:
        ServiceUnavailableException: If the use case is not initialized.
    """
    try:
        use_case = request.app.state.commit_task_mapping_container.commit_task_mapping_use_case

        if use_case is None:
            raise ServiceUnavailableException("Commit task mapper use case is not initialized.")

        return use_case

    except ServiceUnavailableException:
        raise
    except Exception as e:
        logger.exception("Failed to retrieve Commit task mapper use case: %s", str(e))
        raise ServiceUnavailableException("Commit task mapper service is unavailable.") from e
