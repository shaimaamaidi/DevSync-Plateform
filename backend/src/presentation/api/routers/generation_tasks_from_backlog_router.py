"""
ClickUp task generation from sprint backlog API routes.

This module defines API endpoints for generating ClickUp tasks from a sprint backlog.

The API exposes endpoints to:
- Convert a backlog into structured ClickUp tasks
- Associate generated tasks with a ClickUp space
- Return structured task data for downstream processing

Routes:
    POST /generate-tasks-from-backlog: Generate ClickUp tasks from a sprint backlog.
"""

import logging
from fastapi import APIRouter, Depends
from starlette import status

from backend.src.domain.entities.generated_tasks.generated_task_from_backlog import GeneratedTaskFromBacklog
from backend.src.domain.entities.generated_tasks.generated_task_from_backlog_request import GeneratedTaskFromBacklogRequest
from backend.src.domain.ports.input.i_generate_tasks_from_backlog_use_case import IGenerateTasksFromBacklogUseCase
from backend.src.presentation.api.deps import get_generate_task_from_backlog_use_case


logger = logging.getLogger(__name__)


router = APIRouter()


@router.post(
    "/generate-tasks-from-backlog",
    response_model=list[GeneratedTaskFromBacklog],
    status_code=status.HTTP_200_OK,
    summary="Generate ClickUp tasks from sprint backlog",
    description=(
        "Transforms a sprint backlog into structured ClickUp tasks using AI-based extraction. "
        "The generated tasks are formatted for direct integration into ClickUp workflows."
    )
)
def generate_tasks_from_backlog(
    request: GeneratedTaskFromBacklogRequest,
    use_case: IGenerateTasksFromBacklogUseCase = Depends(get_generate_task_from_backlog_use_case),
):
    """
    Generate ClickUp tasks from a sprint backlog.

    This endpoint transforms sprint backlog notes into structured tasks
    suitable for ClickUp. It delegates the generation logic to the application
    use case responsible for LLM-based task extraction.

    Args:
        request (GenerateTasksFromBacklogRequest):
            Request payload containing:
            - sprint_backlog: sprint backlog content
            - space_id: ClickUp workspace identifier
        use_case (IGenerateTasksFromBacklogUseCase): Application use case responsible for generating tasks.

    Returns:
        list[GeneratedTaskFromBacklog]: List of structured ClickUp tasks generated from the backlog.
    """
    logger.info(
        "Generating ClickUp tasks from backlog: space_id=%s.",
        request.space_id,
    )

    tasks = use_case.generate_tasks_from_backlog(
        sprint_backlog=request.sprint_backlog,
        space_id=request.space_id,
    )

    logger.info(
        "ClickUp tasks generated successfully from backlog: space_id=%s, generated_tasks=%d.",
        request.space_id,
        len(tasks),
    )

    return tasks