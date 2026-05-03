"""
ClickUp task generation from meeting summary API routes.

This module defines API endpoints for generating ClickUp tasks from a meeting summary.

The API exposes endpoints to:
- Convert a meeting summary into structured ClickUp tasks
- Associate generated tasks with a ClickUp space
- Return structured task data for downstream processing

Routes:
    POST /generate-tasks-from-summary: Generate ClickUp tasks from a meeting summary.
"""

import logging
from fastapi import APIRouter, Depends

from backend.src.domain.entities.clickup.generated_task import GeneratedTask
from backend.src.domain.entities.generate_tasks_from_summary.generate_tasks_request import GenerateTasksFromSummaryRequest
from backend.src.domain.ports.input.i_generate_task_from_summary_use_case import IGenerateTaskFromSummaryUseCase
from backend.src.presentation.api.deps import get_generate_task_from_summary_use_case


logger = logging.getLogger(__name__)


router = APIRouter()


@router.post("/generate-tasks-from-summary", response_model=list[GeneratedTask])
def generate_tasks_from_summary(
    request: GenerateTasksFromSummaryRequest,
    use_case: IGenerateTaskFromSummaryUseCase = Depends(get_generate_task_from_summary_use_case),
):
    """
    Generate ClickUp tasks from a meeting summary.

    This endpoint transforms unstructured meeting notes into structured tasks
    suitable for ClickUp. It delegates the generation logic to the application
    use case responsible for LLM-based task extraction.

    Args:
        request (GenerateTasksFromSummaryRequest):
            Request payload containing:
            - meeting_summary: raw meeting notes
            - space_id: ClickUp workspace identifier

        use_case (IGenerateTaskFromSummaryUseCase):
            Application use case responsible for generating tasks.

    Returns:
        list[GeneratedTask]:
            List of structured ClickUp tasks generated from the summary.
    """
    logger.info(
        "POST /generate-tasks-from-summary: space_id=%s.",
        request.space_id,
    )

    tasks = use_case.generate_tasks_from_meeting_summary(
        meeting_summary=request.meeting_summary,
        space_id=request.space_id,
    )

    logger.info(
        "POST /generate-tasks-from-summary completed. space_id=%s generated_tasks=%d.",
        request.space_id,
        len(tasks),
    )

    return tasks