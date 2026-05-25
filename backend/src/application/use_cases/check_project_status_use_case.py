"""
Project status use case module.

This module provides the CheckProjectStatusUseCase class, which is responsible for
orchestrating the computation of a project's overall health and activity status.

It aggregates and analyzes data from multiple sources, including ClickUp tasks
and GitHub (commits and deployments), in order to produce a unified, user-facing
project status summary.

The use case performs:
- Extraction and classification of ClickUp tasks (Todo, In Progress, Done)
- Detection of overdue, stale, and potentially unverified tasks
- Retrieval of GitHub commit and deployment activity (if repository is linked)
- Temporal analysis of recent project activity
- Computation of a global project status code and explanatory message

Classes:
    CheckProjectStatusUseCase: Main use case for computing project status.
"""
import asyncio
import logging
import datetime
from typing import List, Optional

from backend.src.domain.entities.check_project_status.overdue_todo_task import OverdueTodoTask
from backend.src.domain.entities.check_project_status.project_status_summary import ProjectStatusSummary, TaskSummary, \
    ProjectStatusCode
from backend.src.domain.entities.clickup.list_with_tasks import ClickUpTask
from backend.src.domain.entities.github.commit import CommitDTO
from backend.src.domain.ports.input.i_check_project_status_use_case import ICheckProjectStatusUseCase
from backend.src.domain.ports.output.clickup.i_clickup_reader import IClickUpReader
from backend.src.domain.ports.output.github.i_github_commit_service import IGitHubCommitService
from backend.src.domain.ports.output.github.i_github_deployment_service import IGitHubDeploymentService
from backend.src.domain.ports.services.project_status_check.stale_task_inspector import IStaleTaskInspector
from backend.src.domain.ports.services.project_status_check.unverified_done_task_inspector import \
    IUnverifiedDoneTaskInspector


logger = logging.getLogger(__name__)


class CheckProjectStatusUseCase(ICheckProjectStatusUseCase):
    """
    Application use case for computing the overall status of a project.

    This use case orchestrates a full project health evaluation by:
    - Retrieving ClickUp workspace structure and extracting all tasks
    - Computing task distribution across statuses (Todo, In Progress, Done)
    - Identifying overdue Todo tasks based on creation time
    - Detecting stale In Progress tasks using recent GitHub commits
    - Verifying recently completed tasks against commit history
    - Fetching GitHub commit and deployment activity (if repository is linked)
    - Determining the latest project activity timestamps
    - Producing a structured ProjectStatusSummary for user consumption

    Attributes:
        _clickup_reader (IClickUpReader): Port used to retrieve ClickUp workspace data.
        _stale_task_inspector (IStaleTaskInspector): Service used to detect stale in-progress tasks.
        _unverified_done_task_inspector (IUnverifiedDoneTaskInspector): Service used to validate completed tasks against GitHub activity.
        _github_commit_service (IGitHubCommitService): Service for retrieving commit history.
        _github_deployment_service (IGitHubDeploymentService): Service for retrieving deployment history.
    """

    _OVERDUE_DAYS = 14

    def __init__(
        self,
        clickup_reader: IClickUpReader,
        stale_task_inspector: IStaleTaskInspector,
        unverified_done_task_inspector: IUnverifiedDoneTaskInspector,
        github_deployment_service: IGitHubDeploymentService,
        github_commit_service: IGitHubCommitService,
    ):
        """
        Initialize the CheckProjectStatusUseCase.

        Args:
            clickup_reader: ClickUp reader port implementation used to retrieve workspace structure.
            stale_task_inspector: Service responsible for detecting stale tasks.
            unverified_done_task_inspector: Service responsible for verifying that recently completed tasks have linked commit evidence.
            github_deployment_service: Service used to fetch GitHub deployment information.
            github_commit_service: Service used to fetch GitHub commit history.
        """
        self._clickup_reader = clickup_reader
        self._stale_task_inspector = stale_task_inspector
        self._unverified_done_task_inspector = unverified_done_task_inspector
        self._github_commit_service = github_commit_service
        self._github_deployment_service = github_deployment_service

    async def get_project_status(self, space_id: str, repo_url: Optional[str]) -> ProjectStatusSummary:
        """
        Compute the overall status of a project.

        This method orchestrates the full project health analysis by:
        - Retrieving all ClickUp tasks for the given space
        - Computing task distribution across statuses (Todo, In Progress, Done)
        - Identifying overdue Todo tasks based on creation date
        - Detecting recently completed tasks and validating them against GitHub activity
        - Fetching GitHub commits and deployments when a repository is linked
        - Determining the latest activity timestamps from GitHub
        - Detecting stale in-progress tasks using recent commit history
        - Evaluating the level of GitHub integration and activity completeness
        - Generating a global project status code and human-readable message

        Args:
            space_id: Identifier of the ClickUp space to analyze.
            repo_url: Optional GitHub repository URL linked to the project.

        Returns:
            ProjectStatusSummary: Structured summary containing:
                - Global project status code
                - Human-readable status message
                - Total number of tasks
                - Task distribution by status
                - Last commit and deployment timestamps (if available)
                - List of overdue Todo tasks
                - List of stale in-progress tasks
                - List of unverified completed tasks
                - GitHub integration and activity indicators
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
        to_do_tasks: List[ClickUpTask] = []
        done_tasks: List[ClickUpTask] = []

        for task in tasks:
            status_counts[task.status] = status_counts.get(task.status, 0) + 1
            if task.status.lower() in ("in progress", "in_progress"):
                in_progress_tasks.append(task)
            if task.status.lower() in ("todo", "to do"):
                to_do_tasks.append(task)
            if task.status.lower() == "done":
                done_tasks.append(task)

        total = len(tasks)

        tasks_summary: List[TaskSummary] = [
            TaskSummary(
                status=status,
                percentage=round((count / total) * 100, 2) if total > 0 else 0.0
            )
            for status, count in status_counts.items()
        ]

        overdue_todo_tasks = []
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        if to_do_tasks:
            overdue_todo_tasks = await self._get_overdue_todo_tasks(to_do_tasks, now)

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

            since = now - datetime.timedelta(days=7)
            last_7_days_commits = await self._github_commit_service.get_commits_between_dates(
                repo_url,
                since=since,
                until=now,
            )

        stale_tasks = []
        if in_progress_tasks and last_7_days_commits:
            inspected =self._stale_task_inspector.inspect_stale_tasks(in_progress_tasks, last_7_days_commits)
            stale_tasks = [
                task for task in inspected
                if task.is_blocked or (not task.is_blocked and task.confidence == "low")
            ]

        recently_done_tasks: List[ClickUpTask] = []
        if done_tasks:
            recently_done_tasks = await self._get_recently_done_tasks(done_tasks, now)

        unverified_done_tasks = []
        if recently_done_tasks and last_7_days_commits:
            inspected = self._unverified_done_task_inspector.verify_done_tasks(recently_done_tasks, last_7_days_commits)
            unverified_done_tasks = [
                task for task in inspected
                if not task.has_commit or (task.has_commit and task.confidence == "low")
            ]

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
            total_tasks=total,
            tasks_summary=tasks_summary,
            last_commit=last_commit_date,
            last_deployment=last_deployment_date,
            overdue_todo_tasks=overdue_todo_tasks,
            stale_tasks=stale_tasks,
            unverified_done_tasks=unverified_done_tasks,
        )

    async def _get_overdue_todo_tasks(
            self,
            todo_tasks: List[ClickUpTask],
            now: datetime.datetime,
    ) -> List[OverdueTodoTask]:
        """
        Identify Todo tasks that have been waiting for more than _OVERDUE_DAYS days.

        Fetches task time context in parallel for all Todo tasks and filters
        those whose creation date exceeds the overdue threshold.

        Args:
            todo_tasks: List of ClickUp tasks currently in Todo status.
            now: Current UTC datetime used as reference for age computation.

        Returns:
            List of OverdueTodoTask for tasks exceeding the overdue threshold.
        """
        results = await asyncio.gather(*[self._fetch_context(task) for task in todo_tasks])

        overdue = []
        for task, context in results:
            date_created: Optional[datetime.datetime] = context.get("date_created")
            if date_created and (now - date_created).days > self._OVERDUE_DAYS:
                days_waiting = (now - date_created).days
                overdue.append(
                    OverdueTodoTask(
                        task_id=task.id,
                        task_name=task.name,
                        task_description=task.description,
                        days_waiting=days_waiting,
                        reason=f"Task has been in 'Todo' status for more than {days_waiting} days with no progress.",
                    )
                )

        return overdue

    async def _get_recently_done_tasks(
            self,
            done_tasks: List[ClickUpTask],
            now: datetime.datetime,
    ) -> List[ClickUpTask]:
        """
        Filter Done tasks that were closed within the last 6 days.

        Fetches task time context in parallel for all Done tasks and retains
        only those whose closing date falls within the recent activity window.
        Tasks closed more than 6 days ago are excluded to ensure temporal
        coherence with the last 7 days commit window.

        Args:
            done_tasks: List of ClickUp tasks currently in Done status.
            now: Current UTC datetime used as reference for recency computation.

        Returns:
            List of ClickUpTask closed within the last 6 days.
        """
        results = await asyncio.gather(*[self._fetch_context(task) for task in done_tasks])

        recently_done = []
        for task, context in results:
            date_closed: Optional[datetime.datetime] = context.get("date_closed")
            if date_closed and (now - date_closed).days <= 6:
                recently_done.append(task)

        return recently_done

    async def _fetch_context(self, task: ClickUpTask) -> tuple[ClickUpTask, dict]:
        task_context = await asyncio.to_thread(
            self._clickup_reader.get_task_time_context, task.id
        )
        return task, task_context
