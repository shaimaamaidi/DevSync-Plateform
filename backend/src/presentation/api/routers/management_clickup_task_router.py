"""
ClickUp task creation, update, and deletion API routes.

This module defines API endpoints for managing ClickUp tasks lifecycle,
including creation, update, and deletion operations.

Routes:
    POST /: Create a new ClickUp task.
    PUT /{task_id}: Update an existing ClickUp task.
    DELETE /{task_id}: Delete a ClickUp task.
"""

import logging

from fastapi import APIRouter, Depends, status

from backend.src.application.use_cases.manage_clickup_task_use_case import ManageClickUpTaskUseCase
from backend.src.domain.entities.clickup.create_task_request import CreateTaskRequest
from backend.src.domain.entities.clickup.list_with_tasks import ClickUpTask
from backend.src.domain.entities.clickup.update_task_request import UpdateTaskRequest
from backend.src.presentation.api.deps import get_create_clickup_task_use_case


logger = logging.getLogger(__name__)


router = APIRouter()


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=ClickUpTask,
    summary="Create a ClickUp task",
    description="Create a new task inside a ClickUp list.",
)
def create_task(
    body: CreateTaskRequest,
    use_case: ManageClickUpTaskUseCase = Depends(get_create_clickup_task_use_case),
) -> ClickUpTask:
    """
    Create a ClickUp task.

    Args:
        body (CreateTaskRequest): Task creation payload.
        use_case (ManageClickUpTaskUseCase): Injected use case.

    Returns:
        ClickUpTask: The created ClickUp task entity containing task metadata returned by the ClickUp API.
    """
    logger.info(
        "Creating ClickUp task: list_id=%s, name=%s.",
        body.list_id,
        body.name,
    )

    result = use_case.create_task(body)

    logger.info(
        "ClickUp task created successfully: list_id=%s, name=%s.",
        body.list_id,
        body.name,
    )

    return result

@router.put(
    "/{space_id}",
    status_code=status.HTTP_200_OK,
    response_model=ClickUpTask,
    summary="Update a ClickUp task",
    description="Update an existing ClickUp task by its identifier.",
)
def update_task(
    space_id: str,
    body: UpdateTaskRequest,
    use_case: ManageClickUpTaskUseCase = Depends(get_create_clickup_task_use_case),
) -> ClickUpTask:
    """
    Update a ClickUp task.

    Args:
        space_id (str): ClickUp space identifier (path param).
        body (UpdateTaskRequest): Task update payload.
        use_case (ManageClickUpTaskUseCase): Injected use case.

    Returns:
        ClickUpTask: The updated ClickUp task entity reflecting the latest state returned by
            the ClickUp API.
    """
    logger.info(
        "Updating ClickUp task: space_id=%s, task_id=%s.",
        space_id,
        body.task_id,
    )

    body_with_space_id: UpdateTaskRequest = body.model_copy(update={"space_id": space_id})
    result = use_case.update_task(body_with_space_id)

    logger.info(
        "ClickUp task updated successfully: space_id=%s, task_id=%s.",
        space_id,
        body_with_space_id.task_id,
    )

    return result


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_200_OK,
    response_model=bool,
    summary="Delete a ClickUp task",
    description="Delete an existing ClickUp task by its identifier.",
)
def delete_task(
    task_id: str,
    use_case: ManageClickUpTaskUseCase = Depends(get_create_clickup_task_use_case),
) -> bool:
    """
    Delete a ClickUp task.

    Args:
        task_id (str): ClickUp task identifier (path param).
        use_case (ManageClickUpTaskUseCase): Injected use case.

    Returns:
        bool: True if the task was successfully deleted.
    """
    logger.info("Deleting ClickUp task: task_id=%s.", task_id)

    result = use_case.delete_task(task_id)

    logger.info("ClickUp task deleted successfully: task_id=%s.", task_id)

    return result