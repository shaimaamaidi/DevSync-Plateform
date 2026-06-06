"""
Commit-to-task traceability API routes.

This module defines API endpoints for mapping a Git commit message
to its most probable corresponding ClickUp task.

The API exposes endpoints to:
- Semantically match a commit message to a ClickUp task
- Return match status and task details when found

Routes:
    POST /find-task-by-commit: Map a commit message to a ClickUp task.
"""

import logging

from fastapi import APIRouter, Depends, status

from backend.src.domain.entities.mapped_commit_task.mapped_commit_task_reponse import MappedCommitTaskResponse
from backend.src.domain.entities.mapped_commit_task.mapped_commit_task_request import MappedCommitTaskRequest
from backend.src.domain.ports.input.i_map_commit_task_use_case import IMapCommitTaskUseCase
from backend.src.presentation.api.deps import get_map_commit_task_use_case


logger = logging.getLogger(__name__)


router = APIRouter()


@router.post(
    "/find-task-by-commit",
    response_model=MappedCommitTaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Map a Git commit message to a ClickUp task",
    description=(
        "Receives a Git commit message and a ClickUp space ID, "
        "then semantically matches the commit to the most probable task "
        "within the given space. Returns the match status and task details if found."
    ),
)
async def find_task_by_commit(
    request: MappedCommitTaskRequest,
    use_case: IMapCommitTaskUseCase = Depends(get_map_commit_task_use_case),
) -> MappedCommitTaskResponse:
    """
    Map a Git commit message to a ClickUp task.

    This endpoint delegates the semantic matching logic to the application
    use case. It always returns HTTP 200 with a structured response indicating
    whether a matching task was found, not found, or the space was empty.

    All domain exceptions are handled globally via the application's exception handler.

    Args:
        request (FindTaskByCommitRequest):
            Request payload containing:
            - commit: Git commit message to match
            - space_id: ClickUp space identifier to search within

        use_case (IMapCommitTaskUseCase): Application use case responsible for commit-task mapping.

    Returns:
        MappedCommitTaskResponse:
            Structured response containing:
            - status: FOUND | NOT_FOUND | CLICK_UP_EMPTY
            - message: Human-readable description of the result
            - task: Matched ClickUp task details, or null if not found
    """
    logger.info(
        "Finding ClickUp task for commit: space_id=%s, commit=%s.",
        request.space_id,
        request.commit,
    )

    result = await use_case.map_commit_task(
        commit=request.commit,
        space_id=request.space_id,
    )

    logger.info(
        "Commit-to-task mapping completed: space_id=%s, status=%s.",
        request.space_id,
        result.status,
    )

    return result