"""
Domain DTO for weekly project summary response.

This module defines the WeeklyProjectSummaryResponse DTO used to represent
a complete weekly overview of a project.

It aggregates both raw activity data and LLM-generated summaries, including:
- ClickUp task activity (created, in progress, completed)
- GitHub commits from the last 7 days
- GitHub deployments from the last 7 days
- Natural language summaries of commits and deployments

This DTO is used as the final output of the weekly project summary use case.

Main classes:
    WeeklyProjectSummaryResponse
"""
from enum import Enum
from typing import List

from pydantic import BaseModel

from backend.src.domain.entities.clickup.list_with_tasks import ClickUpTask
from backend.src.domain.entities.github.commit import CommitDTO
from backend.src.domain.entities.github.deployment import DeploymentDTO


class WeeklyProjectSummaryStatus(str, Enum):
    FULL = "FULL"
    NO_GITHUB = "NO_GITHUB"
    CLICKUP_EMPTY = "CLICKUP_EMPTY"
    NO_GITHUB_AND_CLICKUP_EMPTY = "NO_GITHUB_AND_CLICKUP_EMPTY"

class WeeklyProjectSummaryResponse(BaseModel):
    """
    Representation of a complete weekly project activity report.

    This model aggregates structured task data from ClickUp and
    development activity from GitHub, along with AI-generated summaries.

    Attributes:
        created_tasks: Tasks created during the last 7 days.
        in_progress_tasks: Tasks moved to or currently in progress during the last 7 days.
        done_tasks: Tasks completed during the last 7 days.
        last_7_days_deployments: GitHub deployments executed in the last 7 days.
        deployments_summary: AI-generated narrative summarizing deployment activity.
        last_7_days_commits: GitHub commits made in the last 7 days.
        commits_summary: AI-generated narrative summarizing commit activity.
    """
    status: WeeklyProjectSummaryStatus
    message: str
    created_tasks: List[ClickUpTask] = []
    in_progress_tasks: List[ClickUpTask] = []
    done_tasks: List[ClickUpTask] = []
    last_7_days_deployments: List[DeploymentDTO] = []
    deployments_summary: str
    last_7_days_commits: List[CommitDTO] = []
    commits_summary: str