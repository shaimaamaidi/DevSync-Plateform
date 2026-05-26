"""
ClickUp save backlog tasks API routes.

This module defines API endpoints for saving verified backlog tasks into ClickUp.

The API exposes endpoints to:
- Persist verified backlog tasks into a ClickUp space
- Apply create/update operations based on verification results
- Resolve assignees from human-readable names to ClickUp members
- Confirm successful synchronization with ClickUp

Routes:
    POST /save: Save verified tasks into a ClickUp space.
"""

import logging

from fastapi import APIRouter, Depends, status, Response

from backend.src.domain.entities.saved_tasks_request.save_backlog_tasks_request import SaveBacklogTasksRequest
from backend.src.domain.ports.input.i_save_backlog_tasks_use_case import ISaveBacklogTasksInClickUpUseCase
from backend.src.presentation.api.deps import get_save_backlog_tasks_use_case


logger = logging.getLogger(__name__)


router = APIRouter()


@router.post(
    "/save-backlog-tasks",
    response_class=Response,
    status_code=status.HTTP_201_CREATED,
    summary="Save verified backlog tasks into ClickUp",
    description=(
        "Receives a list of verified backlog tasks and applies them (create or update) "
        "into the specified ClickUp space. Assignees are resolved from Arabic names "
        "to ClickUp member IDs when applicable."
    ),
)
def save_backlog_tasks_to_clickup(
    request: SaveBacklogTasksRequest,
    use_case: ISaveBacklogTasksInClickUpUseCase = Depends(get_save_backlog_tasks_use_case),
) -> Response:
    """
    Save verified tasks into ClickUp.

    This endpoint delegates the persistence logic to the application use case.
    It applies create/update operations on ClickUp tasks based on the verification
    results and ensures proper assignment resolution for task assignees.

    All domain exceptions are handled globally via the application's exception handler.

    Args:
        request (SaveBacklogTasksRequest):
            Request payload containing:
            - tasks: list of verified tasks to persist
            - space_id: ClickUp workspace identifier
            - ignore_names: optional list of names to ignore during processing
            - ignore_mails: optional list of emails to ignore during processing

        use_case (ISaveBacklogTasksInClickUpUseCase): Application use case responsible for ClickUp persistence logic.

    Returns:
        None:
            This endpoint does not return any response body.
            It only confirms successful execution via HTTP 201 Created status.
    """
    logger.info(
        "Saving verified backlog tasks into ClickUp: space_id=%s, total_tasks=%d.",
        request.space_id,
        len(request.tasks),
    )

    use_case.save_backlog_tasks_to_clickup(
        tasks=request.tasks,
        space_id=request.space_id,
        ignore_names=request.ignore_names,
        ignore_mails=request.ignore_mails,
    )

    logger.info(
        "Backlog tasks saved successfully: space_id=%s, total_tasks=%d.",
        request.space_id,
        len(request.tasks),
    )

    return Response(status_code=status.HTTP_201_CREATED)