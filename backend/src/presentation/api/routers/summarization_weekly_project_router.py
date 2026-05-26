"""
Weekly project summary API routes.

This module defines API endpoints for retrieving a weekly summary of a ClickUp project
by aggregating task activity and optionally cross-referencing with GitHub commits and deployments.

The API exposes endpoints to:
- Compute the weekly summary of a project based on ClickUp tasks and GitHub data

Routes:
    POST /summary: Compute the weekly summary of a project.
"""

import logging

from fastapi import APIRouter, Depends, status

from backend.src.domain.entities.shared.project_space_request import ProjectSpaceRequest
from backend.src.domain.entities.weekly_project_summary.weekly_project_summary_response import WeeklyProjectSummaryResponse
from backend.src.domain.ports.input.i_summarize_weekly_project_summary_use_case import ISummarizeWeeklyProjectUseCase
from backend.src.presentation.api.deps import get_weekly_project_summary_use_case


logger = logging.getLogger(__name__)


router = APIRouter()


@router.post(
    "/summary",
    response_model=WeeklyProjectSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Compute the weekly summary of a project",
    description=(
        "Receives a ClickUp space identifier and an optional GitHub repository URL. "
        "Aggregates task activity from the last 7 days including created, in-progress, and completed tasks. "
        "Optionally enriches the summary with GitHub commit and deployment activity. "
        "Returns a structured weekly summary including task movements, commit and deployment history, "
        "and AI-generated narratives for commits and deployments when a repository is linked."
    ),
)
async def summarize_weekly_project(
    body: ProjectSpaceRequest,
    use_case: ISummarizeWeeklyProjectUseCase = Depends(get_weekly_project_summary_use_case),
) -> WeeklyProjectSummaryResponse:
    """
    Compute the weekly summary of a project.

    This endpoint delegates the weekly summary computation to the application use case.
    It fetches all ClickUp tasks from the given space, identifies task movements over
    the last 7 days, and optionally cross-references GitHub commit and deployment
    activity if a repository URL is provided.

    All domain exceptions are handled globally via the application's exception handler.

    Args:
        body (ProjectSpaceRequest):
            Request payload containing:
            - space_id: ClickUp space identifier to analyze
            - repo_url: optional GitHub repository URL linked to the project

        use_case (ISummarizeWeeklyProjectUseCase): Application use case responsible for weekly summary computation.

    Returns:
        WeeklyProjectSummaryResponse:
            Structured response containing:
            - created_tasks: tasks created during the last 7 days
            - in_progress_tasks: tasks that moved to in-progress during the last 7 days
            - done_tasks: tasks completed during the last 7 days
            - last_7_days_commits: list of GitHub commits from the last 7 days (if available)
            - commits_summary: AI-generated narrative summarizing commit activity (if available)
            - last_7_days_deployments: list of GitHub deployments from the last 7 days (if available)
            - deployments_summary: AI-generated narrative summarizing deployment activity (if available)
    """
    logger.info(
        "Computing weekly project summary: space_id=%s, repo_url=%s.",
        body.space_id,
        body.repo_url or "none",
    )

    result = await use_case.get_weekly_project_summary(
        space_id=body.space_id,
        repo_url=body.repo_url,
    )

    logger.info(
        "Weekly project summary computation completed: space_id=%s, tasks_done=%d, commits=%d, deployments=%d.",
        body.space_id,
        len(result.done_tasks),
        len(result.last_7_days_commits),
        len(result.last_7_days_deployments),
    )

    return result