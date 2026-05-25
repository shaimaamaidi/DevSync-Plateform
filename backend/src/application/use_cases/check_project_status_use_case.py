"""
Project status use case module.

This module provides the CheckProjectStatusUseCase class, which is responsible for
orchestrating the computation of a project’s health and activity status.

It aggregates data from ClickUp tasks and GitHub (commits and deployments),
analyzes task activity, detects stale tasks, and produces a structured
user-facing project status summary.

Classes:
    CheckProjectStatusUseCase: Main use case for computing project status.
"""

import logging
import datetime
from typing import List, Optional

from backend.src.domain.entities.check_project_status.project_status_summary import ProjectStatusSummary, TaskSummary, \
    ProjectStatusCode
from backend.src.domain.entities.clickup.list_with_tasks import ClickUpTask
from backend.src.domain.entities.github.commit import CommitDTO
from backend.src.domain.ports.input.i_check_project_status_use_case import ICheckProjectStatusUseCase
from backend.src.domain.ports.output.clickup.i_clickup_reader import IClickUpReader
from backend.src.domain.ports.output.github.i_github_commit_service import IGitHubCommitService
from backend.src.domain.ports.output.github.i_github_deployment_service import IGitHubDeploymentService
from backend.src.domain.ports.services.stale_task_inspection.stale_task_inspector import IStaleTaskInspector


logger = logging.getLogger(__name__)


class CheckProjectStatusUseCase(ICheckProjectStatusUseCase):
    """
    Application use case for computing project status.

    This use case orchestrates the full project health evaluation by:
    - Fetching ClickUp workspace structure and extracting all tasks
    - Computing task distribution and progress metrics
    - Retrieving GitHub commit and deployment information (if repository is linked)
    - Detecting stale in-progress tasks based on recent commit activity
    - Producing a structured ProjectStatusSummary with a human-readable message

    Attributes:
        _clickup_reader (IClickUpReader): Port used to fetch ClickUp workspace data.
        _stale_task_inspector (IStaleTaskInspector): Service used to detect stale tasks.
        _github_commit_service (IGitHubCommitService): Service for retrieving GitHub commits.
        _github_deployment_service (IGitHubDeploymentService): Service for retrieving deployments.
    """

    def __init__(
        self,
        clickup_reader: IClickUpReader,
        stale_task_inspector: IStaleTaskInspector,
        github_deployment_service: IGitHubDeploymentService,
        github_commit_service: IGitHubCommitService,
    ):
        """
        Initialize the CheckProjectStatusUseCase.

        Args:
            clickup_reader: ClickUp reader port implementation used to retrieve workspace structure.
            stale_task_inspector: Service responsible for detecting stale tasks.
            github_deployment_service: Service used to fetch GitHub deployment information.
            github_commit_service: Service used to fetch GitHub commit history.
        """
        self._clickup_reader = clickup_reader
        self._stale_task_inspector = stale_task_inspector
        self._github_commit_service = github_commit_service
        self._github_deployment_service = github_deployment_service

    async def get_project_status(self, space_id: str, repo_url: Optional[str]) -> ProjectStatusSummary:
        """
        Compute the overall status of a project.

        This method:
        - Retrieves all ClickUp tasks from the given space
        - Computes task distribution by status
        - Identifies in-progress tasks for activity analysis
        - Fetches GitHub commits and deployments if a repository is linked
        - Determines last activity timestamps (commits and deployments)
        - Detects stale tasks based on recent commit history
        - Computes a global project status (GitHub integration + activity level)
        - Returns a structured summary for user consumption

        Args:
            space_id: Identifier of the ClickUp space to analyze.
            repo_url: Optional GitHub repository URL linked to the project.

        Returns:
            ProjectStatusSummary: Structured summary containing:
                - Global project status code
                - Human-readable status message
                - Task distribution summary
                - Last commit and deployment dates (if available)
                - List of stale tasks (if any detected)
                - GitHub integration flag
        """
        logger.info("Fetching project status. space_id=%s.", space_id)

        folder_with_tasks = self._clickup_reader.get_space_full_structure(space_id)

        tasks =[
            task
            for folder in folder_with_tasks
            for lst in folder.lists
            for task in lst.tasks
        ]

        status_counts: dict[str, int] = {}
        in_progress_tasks: List[ClickUpTask] = []
        for task in tasks:
            status_counts[task.status] = status_counts.get(task.status, 0) + 1
            if task.status.lower() in ("in progress", "in_progress"):
                in_progress_tasks.append(task)

        total = len(tasks)

        tasks_summary: List[TaskSummary] = [
            TaskSummary(
                status=status,
                percentage=round((count / total) * 100, 2) if total > 0 else 0.0
            )
            for status, count in status_counts.items()
        ]

        last_commit_date: Optional[datetime] = None
        last_deployment_date: Optional[datetime] = None
        last_7_days_commits: List[CommitDTO] = []

        if repo_url:
            commit = self._github_commit_service.get_commits(repo_url, max_commits=1)
            if commit:
                last_commit_date = commit[0].date

            deployment = self._github_deployment_service.get_deployments(repo_url, max_deployments=1)
            if deployment:
                last_deployment_date = deployment[0].created_at

            now = datetime.datetime.now(tz=datetime.timezone.utc)
            since = now - datetime.timedelta(days=7)
            last_7_days_commits = await self._github_commit_service.get_commits_between_dates(
                repo_url,
                since=since,
                until=now,
            )

        stale_tasks = []
        if in_progress_tasks and last_7_days_commits:
            stale_tasks =self._stale_task_inspector.inspect_stale_tasks(in_progress_tasks, last_7_days_commits)

        if not repo_url:
            status = ProjectStatusCode.NO_GITHUB
            message = (
                "This project is not linked to any GitHub repository. "
                "The status below is based solely on ClickUp task data."
            )

        elif not last_commit_date and not last_deployment_date:
            status = ProjectStatusCode.NO_GITHUB_ACTIVITY
            message = (
                "The linked GitHub repository has no recorded commits or deployments yet. "
                "The status below is based solely on ClickUp task data."
            )

        elif not last_commit_date:
            status = ProjectStatusCode.NO_COMMITS
            message = (
                "The GitHub repository is linked, but no commits have been detected. "
                "Deployments exist, but commit history is missing. "
                "The status below is based on ClickUp task data and deployment activity."
            )

        elif not last_deployment_date:
            status = ProjectStatusCode.NO_DEPLOYMENTS
            message = (
                "The GitHub repository is linked, but no deployments have been detected. "
                "Commits exist, but deployment history is missing. "
                "The status below is based on ClickUp task data and commit activity."
            )

        else:
            status = ProjectStatusCode.FULL
            message = (
                "The project is fully integrated and actively tracked. "
                "Both GitHub commits and deployments are available and up to date. "
                "The status below is based on ClickUp tasks combined with GitHub commit and deployment activity."
            )

        logger.info(
            "Project status computation completed successfully: space_id=%s status=%s tasks=%d.",
            space_id,
            status,
            len(tasks),
        )

        return ProjectStatusSummary(
            status=status,
            message=message,
            has_github_integration=repo_url is not None,
            tasks_summary=tasks_summary,
            last_commit=last_commit_date,
            last_deployment=last_deployment_date,
            stale_tasks=stale_tasks,
        )