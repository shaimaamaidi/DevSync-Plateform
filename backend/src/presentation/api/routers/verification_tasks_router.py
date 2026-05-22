"""
ClickUp task verification API routes.

This module defines API endpoints for verifying generated tasks against existing
ClickUp tasks.

The API exposes endpoints to:
- Verify a batch of generated tasks against a ClickUp space
- Determine whether tasks should be created or updated
- Return a structured verification result for downstream processing

Routes:
    POST /verify: Verify generated tasks against existing ClickUp tasks.
"""

import logging

from fastapi import APIRouter, Depends, status

from backend.src.domain.entities.verify_tasks.verify_tasks_request import VerifyTasksRequest
from backend.src.domain.entities.verify_tasks.verify_tasks_response import VerifyTasksResponse
from backend.src.domain.ports.input.i_verify_tasks_use_case import IVerifyTasksUseCase
from backend.src.presentation.api.deps import get_verify_tasks_use_case


logger = logging.getLogger(__name__)


router = APIRouter()


@router.post(
    "/verify",
    response_model=VerifyTasksResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify generated tasks against existing ClickUp tasks",
    description=(
        "Receives a list of generated tasks and a ClickUp space identifier. "
        "Compares them folder by folder against existing tasks and returns "
        "a list of verified tasks with create or update actions."
    ),
)
def verify_tasks(
    request: VerifyTasksRequest,
    use_case: IVerifyTasksUseCase = Depends(get_verify_tasks_use_case),
) -> VerifyTasksResponse:
    """
    Verify generated tasks against existing ClickUp tasks.

    This endpoint delegates the verification process to the application use case.
    It ensures that each generated task is compared with existing ClickUp data
    to determine the appropriate action (create or update).

    All domain exceptions are handled globally via the application's exception handler.

    Args:
        request (VerifyTasksRequest):
            Request payload containing:
            - tasks: list of generated tasks
            - space_id: ClickUp space identifier

        use_case (IVerifyTasksUseCase): Application use case responsible for task verification logic.

    Returns:
        VerifyTasksResponse:
            Structured response containing:
            - total: number of verified tasks
            - tasks: list of tasks with their computed actions
    """
    logger.info(
        "Verifying generated ClickUp tasks: space_id=%s, total_tasks=%d.",
        request.space_id,
        len(request.tasks),
    )

    results = use_case.verify_tasks(
        tasks=request.tasks,
        space_id=request.space_id,
    )

    logger.info(
        "ClickUp tasks verification completed: space_id=%s total_verified=%d create=%d update=%d.",
        request.space_id,
        len(results),
        sum(1 for r in results if r.action == "create"),
        sum(1 for r in results if r.action == "update"),
    )

    return VerifyTasksResponse(
        total=len(results),
        tasks=results,
    )