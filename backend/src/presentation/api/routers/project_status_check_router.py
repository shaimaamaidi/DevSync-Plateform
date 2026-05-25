"""
Project status check API routes.

This module defines API endpoints for checking the overall status of a ClickUp project
by aggregating task data and optionally cross-referencing with GitHub activity.

The API exposes endpoints to:
- Compute the overall status of a project based on ClickUp tasks and GitHub data

Routes:
    POST /status: Compute the overall status of a project.
"""

import logging

from fastapi import APIRouter, Depends, status

from backend.src.domain.entities.check_project_status.checked_project_status_request import CheckedProjectStatusRequest
from backend.src.domain.entities.check_project_status.project_status_summary import ProjectStatusSummary
from backend.src.domain.ports.input.i_check_project_status_use_case import ICheckProjectStatusUseCase
from backend.src.presentation.api.deps import get_check_project_status_use_case


logger = logging.getLogger(__name__)


router = APIRouter()


@router.post(
    "/status",
    response_model=ProjectStatusSummary,
    status_code=status.HTTP_200_OK,
    summary="Compute the overall status of a project",
    description=(
        "Receives a ClickUp space identifier and an optional GitHub repository URL. "
        "Aggregates task distribution and progress metrics from ClickUp, "
        "and optionally enriches the analysis with GitHub commit and deployment activity. "
        "Returns a structured project status summary including a global status code, "
        "a human-readable message, task distribution, last activity dates, and any stale tasks detected."
    ),
)
async def check_project_status(
    body: CheckedProjectStatusRequest,
    use_case: ICheckProjectStatusUseCase = Depends(get_check_project_status_use_case),
) -> ProjectStatusSummary:
    """
    Compute the overall status of a project.

    This endpoint delegates the status computation to the application use case.
    It fetches all ClickUp tasks from the given space, computes task distribution
    and progress metrics, and optionally cross-references GitHub commit and deployment
    activity if a repository URL is provided.

    All domain exceptions are handled globally via the application's exception handler.

    Args:
        body (CheckedProjectStatusRequest):
            Request payload containing:
            - space_id: ClickUp space identifier to analyze
            - repo_url: optional GitHub repository URL linked to the project

        use_case (CheckProjectStatusUseCase): Application use case responsible for project status computation.

    Returns:
        ProjectStatusSummary:
            Structured response containing:
            - status: global project status code
            - message: human-readable description of the project status
            - has_github_integration: whether a GitHub repository is linked
            - tasks_summary: task distribution by status with percentages
            - last_commit: date of the most recent GitHub commit (if available)
            - last_deployment: date of the most recent GitHub deployment (if available)
            - stale_tasks: list of in-progress tasks with no recent commit activity (if any)
    """
    logger.info(
        "Computing project status: space_id=%s, repo_url=%s.",
        body.space_id,
        body.repo_url or "none",
    )

    result = await use_case.get_project_status(
        space_id=body.space_id,
        repo_url=body.repo_url,
    )

    logger.info(
        "Project status computation completed: space_id=%s, status=%s, tasks=%d.",
        body.space_id,
        result.status,
        len(result.tasks_summary),
    )

    return result