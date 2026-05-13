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

from backend.src.application.use_cases.clickup_task_creation_use_case import ClickUpTaskCreationUseCase
from backend.src.domain.entities.clickup.create_task_request import CreateTaskRequest
from backend.src.domain.entities.clickup.update_task_request import UpdateTaskRequest
from backend.src.presentation.api.deps import get_clickup_task_creation_use_case


logger = logging.getLogger(__name__)


router = APIRouter()


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Create a ClickUp task",
    description="Create a new task inside a ClickUp list.",
)
def create_task(
    body: CreateTaskRequest,
    use_case: ClickUpTaskCreationUseCase = Depends(get_clickup_task_creation_use_case),
) -> None:
    """
    Create a ClickUp task.

    Args:
        body (CreateTaskRequest): Task creation payload.
        use_case (ClickUpTaskCreationUseCase): Injected use case.
    """
    logger.info(
        "POST /clickup/tasks/manage. list_id=%s name=%s.",
        body.list_id,
        body.name,
    )

    use_case.create_task(body)


@router.put(
    "/{task_id}",
    status_code=status.HTTP_200_OK,
    summary="Update a ClickUp task",
    description="Update an existing ClickUp task by its identifier.",
)
def update_task(
    task_id: str,
    body: UpdateTaskRequest,
    use_case: ClickUpTaskCreationUseCase = Depends(get_clickup_task_creation_use_case),
) -> None:
    """
    Update a ClickUp task.

    Args:
        task_id (str): ClickUp task identifier (path param).
        body (UpdateTaskRequest): Task update payload.
        use_case (ClickUpTaskCreationUseCase): Injected use case.
    """
    logger.info("PUT /clickup/tasks/manage/%s.", task_id)

    body.task_id = task_id

    use_case.update_task(body)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a ClickUp task",
    description="Delete an existing ClickUp task by its identifier.",
)
def delete_task(
    task_id: str,
    use_case: ClickUpTaskCreationUseCase = Depends(get_clickup_task_creation_use_case),
) -> None:
    """
    Delete a ClickUp task.

    Args:
        task_id (str): ClickUp task identifier (path param).
        use_case (ClickUpTaskCreationUseCase): Injected use case.
    """
    logger.info("DELETE /clickup/tasks/manage/%s.", task_id)

    use_case.delete_task(task_id)