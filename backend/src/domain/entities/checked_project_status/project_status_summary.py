"""
Domain DTO for project status summary.

This module defines the ProjectStatusSummary DTO used to represent
a global synthesis of a project's health and activity. It aggregates
information from ClickUp tasks, GitHub commits, and deployments to
produce a unified project status view.

Main classes:
    ProjectStatusCode, TaskSummary, ProjectStatusSummary
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel

from backend.src.domain.entities.checked_project_status.inspected_stale_task_result import InspectedStaleTaskResult
from backend.src.domain.entities.checked_project_status.inspected_unverified_done_task_result import \
    InspectedUnverifiedDoneTaskResult
from backend.src.domain.entities.checked_project_status.overdue_todo_task import OverdueTodoTask


class ProjectStatusCode(str, Enum):
    """
    Enumeration of possible high-level project status states.

    Attributes:
        FULL: Project has full activity (commits, deployments, tasks).
        NO_GITHUB: No GitHub repository is linked to the project.
        NO_COMMITS: GitHub repository exists but has no commits.
        NO_DEPLOYMENTS: GitHub repository exists but has no deployments.
        NO_GITHUB_ACTIVITY: Repository exists but shows no activity.
        NO_GITHUB_AND_CLICKUP_EMPTY: No GitHub repository is linked and the click up is empty.
    """
    FULL = "full"
    NO_GITHUB = "no_github"
    NO_COMMITS = "no_commits"
    NO_DEPLOYMENTS = "no_deployments"
    NO_GITHUB_ACTIVITY = "no_github_activity"
    CLICKUP_EMPTY = "CLICKUP_EMPTY"
    NO_GITHUB_AND_CLICKUP_EMPTY = "NO_GITHIB_AND_CLICKUP_EMPTY"


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
    - Stale or blocked in-progress tasks analysis
    - Unverified recently completed tasks analysis
    - Overdue todo tasks analysis

    It provides a high-level view of project health.

    Attributes:
        status: Global project status code.
        message: Human-readable explanation of the current status.
        total_tasks: Total number of tasks in the project.
        tasks_summary: Breakdown of task statuses and completion rates.
        last_commit: Timestamp of the most recent GitHub commit, or None if unavailable.
        last_deployment: Timestamp of the most recent GitHub deployment, or None if unavailable.
        overdue_todo_tasks: List of Todo tasks waiting for more than 14 days with no progress.
        stale_tasks: List of in-progress tasks with no related commit activity in the last 7 days.
        unverified_done_tasks: List of recently completed tasks with no linked commit evidence.
    """
    status: ProjectStatusCode
    message: str
    total_tasks: int
    tasks_summary: List[TaskSummary] = []
    last_commit: Optional[datetime] = None
    last_deployment: Optional[datetime] = None
    overdue_todo_tasks: List[OverdueTodoTask] = []
    stale_tasks: List[InspectedStaleTaskResult] = []
    unverified_done_tasks: List[InspectedUnverifiedDoneTaskResult] = []
