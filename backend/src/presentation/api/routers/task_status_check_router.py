"""
Task status check API routes.

This module defines API endpoints for checking the status of ClickUp tasks
by cross-referencing task details with GitHub commits and deployments.

The API exposes endpoints to:
- Search for ClickUp tasks matching a user question
- Synthesize the completion status of a task using GitHub data

Routes:
    POST /search: Search for ClickUp tasks matching a user question.
    POST /synthesize: Synthesize the completion status of a ClickUp task.
"""

import logging

from fastapi import APIRouter, Depends, status

from backend.src.domain.entities.check_task_status.task_search_request import TaskSearchRequest
from backend.src.domain.entities.check_task_status.task_search_response import TaskSearchResponse
from backend.src.domain.entities.check_task_status.synthesized_task_status_request import SynthesizedTaskStatusRequest
from backend.src.domain.entities.check_task_status.synthesized_task_status_result import SynthesizedTaskStatusResult
from backend.src.domain.ports.input.task_status_check.i_search_task_use_case import ISearchTaskUseCase
from backend.src.domain.ports.input.task_status_check.i_synthesize_task_status_use_case import ISynthesizeTaskStatusUseCase
from backend.src.presentation.api.deps import get_search_task_use_case, get_synthesize_task_status_use_case


logger = logging.getLogger(__name__)


router = APIRouter()


@router.post(
    "/search",
    response_model=TaskSearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Search for ClickUp tasks matching a user question",
    description=(
        "Receives a user question and a ClickUp space identifier. "
        "Searches semantically for matching tasks and returns a message with 0, 1, or up to 3 candidates. "
        "The frontend uses the result to ask for confirmation, prompt the user to choose, or ask to rephrase."
    ),
)
def search_task(
    body: TaskSearchRequest,
    use_case: ISearchTaskUseCase = Depends(get_search_task_use_case),
) -> TaskSearchResponse:
    """
    Search for ClickUp tasks matching a user question.

    This endpoint delegates the search process to the application use case.
    It performs semantic matching against all tasks in the given ClickUp space
    and returns a structured response with a message and matching task candidates.

    All domain exceptions are handled globally via the application's exception handler.

    Args:
        body (TaskSearchRequest):
            Request payload containing:
            - question: user question describing the task
            - space_id: ClickUp space identifier

        use_case (ISearchTaskUseCase): Application use case responsible for task search logic.

    Returns:
        TaskSearchResponse:
            Structured response containing:
            - response: message to display to the user
            - task: list of matching ClickUp tasks (0, 1, or up to 3)
    """
    logger.info(
        "Searching ClickUp tasks: space_id=%s, question=%s.",
        body.space_id,
        body.question,
    )

    result = use_case.search_task(
        question=body.question,
        space_id=body.space_id,
    )

    logger.info(
        "ClickUp task search completed: space_id=%s, tasks_found=%d.",
        body.space_id,
        len(result.task),
    )

    return result


@router.post(
    "/synthesize",
    response_model=SynthesizedTaskStatusResult,
    status_code=status.HTTP_200_OK,
    summary="Synthesize the completion status of a ClickUp task",
    description=(
        "Receives a ClickUp task and an optional GitHub repository URL. "
        "Cross-references the task details with GitHub commits and deployments "
        "to determine whether the task is truly completed. "
        "If no repository URL is provided, the analysis is based solely on the ClickUp status."
    ),
)
async def synthesize_task_status(
    body: SynthesizedTaskStatusRequest,
    use_case: ISynthesizeTaskStatusUseCase = Depends(get_synthesize_task_status_use_case),
) -> SynthesizedTaskStatusResult:
    """
    Synthesize the completion status of a ClickUp task.

    This endpoint delegates the synthesis process to the application use case.
    It fetches GitHub commits and deployments if a repository URL is provided,
    then uses an LLM to cross-reference all available evidence and return
    a structured synthesis result.

    All domain exceptions are handled globally via the application's exception handler.

    Args:
        body (SynthesizedTaskStatusRequest):
            Request payload containing:
            - task: ClickUp task to analyze
            - repo_url: optional GitHub repository URL

        use_case (ISynthesizeTaskStatusUseCase): Application use case responsible for task status synthesis.

    Returns:
        SynthesizedTaskStatusResult:
            Structured response containing:
            - is_completed: whether the task is considered completed
            - confidence: confidence level of the analysis (high, medium, low)
            - summary: one-sentence explanation of the conclusion
            - evidence: list of concrete facts supporting the conclusion
    """
    logger.info(
        "Synthesizing ClickUp task status: task_id=%s, repo_url=%s.",
        body.task.id,
        body.repo_url or "none",
    )

    result = await use_case.analyze_task_status(
        task=body.task,
        repo_url=body.repo_url,
    )

    logger.info(
        "ClickUp task status synthesis completed: task_id=%s, is_completed=%s, confidence=%s.",
        body.task.id,
        result.is_completed,
        result.confidence,
    )

    return result