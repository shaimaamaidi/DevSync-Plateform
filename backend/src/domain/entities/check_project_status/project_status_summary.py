"""
Domain DTO for project status summary.

This module defines the ProjectStatusSummary DTO used to represent
a global synthesis of a project's health and activity. It aggregates
information from ClickUp tasks, GitHub commits, and deployments to
produce a unified project status view.

Main classes:
    ProjectStatusCode
    TaskSummary
    ProjectStatusSummary
"""

from datetime import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel

from backend.src.domain.entities.check_project_status.inspected_stale_task_result import InspectedStaleTaskResult


class ProjectStatusCode(str, Enum):
    """
    Enumeration of possible high-level project status states.

    Attributes:
        FULL: Project has full activity (commits, deployments, tasks).
        NO_GITHUB: No GitHub repository is linked to the project.
        NO_COMMITS: GitHub repository exists but has no commits.
        NO_DEPLOYMENTS: GitHub repository exists but has no deployments.
        NO_GITHUB_ACTIVITY: Repository exists but shows no activity.
    """
    FULL = "full"
    NO_GITHUB = "no_github"
    NO_COMMITS = "no_commits"
    NO_DEPLOYMENTS = "no_deployments"
    NO_GITHUB_ACTIVITY = "no_github_activity"


class TaskSummary(BaseModel):
    """
    Summary of task completion state.

    Attributes:
        status: Task status label (e.g., done, in_progress).
        percentage: Completion percentage of tasks for this status.
    """
    status: str
    percentage: float


class ProjectStatusSummary(BaseModel):
    """
    Representation of a global project status summary.

    This DTO aggregates multiple sources of information including:
    - ClickUp task progress
    - GitHub commit activity
    - Deployment history
    - Stale or blocked tasks analysis

    It provides a high-level view of project health.

    Attributes:
        status: Global project status code.
        message: Human-readable explanation of the current status.
        tasks_summary: Breakdown of task statuses and completion rates.
        last_commit: Timestamp of the most recent commit.
        last_deployment: Timestamp of the most recent deployment.
        stale_tasks: List of detected stale or blocked tasks.
        has_github_integration: Indicates whether GitHub is linked.
    """
    status: ProjectStatusCode
    message: str
    tasks_summary: List[TaskSummary]
    last_commit: datetime
    last_deployment: datetime
    stale_tasks: List[InspectedStaleTaskResult]
    has_github_integration: bool