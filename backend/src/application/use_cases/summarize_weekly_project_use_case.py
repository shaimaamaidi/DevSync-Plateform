"""
Application use case module for weekly project summary.

This module provides the SummarizeWeeklyProjectUseCase class, which is responsible for
orchestrating the generation of a weekly project activity summary.

It aggregates and analyzes data from multiple sources, including ClickUp tasks,
GitHub commits, and deployments, in order to produce a structured weekly report
for user consumption.

The use case performs:
- Extraction of ClickUp tasks within a given space
- Classification of tasks by lifecycle changes during the last 7 days
- Retrieval of GitHub commits and deployments for the same period
- Generation of natural language summaries for commits and deployments
- Assembly of a structured WeeklyProjectSummaryResponse

Classes:
    SummarizeWeeklyProjectUseCase: Main use case for weekly project summary generation.
"""

import asyncio
import logging
import datetime
from typing import List, Optional

from backend.src.application.use_cases.shared.clickup_task_context_fetcher import fetch_task_context
from backend.src.domain.entities.clickup.list_with_tasks import ClickUpTask
from backend.src.domain.entities.github.commit import CommitDTO
from backend.src.domain.entities.github.deployment import DeploymentDTO
from backend.src.domain.entities.weekly_project_summary.weekly_project_summary_response import \
    WeeklyProjectSummaryResponse, WeeklyProjectSummaryStatus
from backend.src.domain.ports.input.i_summarize_weekly_project_summary_use_case import ISummarizeWeeklyProjectUseCase
from backend.src.domain.ports.output.clickup.i_clickup_reader import IClickUpReader
from backend.src.domain.ports.output.github.i_github_commit_service import IGitHubCommitService
from backend.src.domain.ports.output.github.i_github_deployment_service import IGitHubDeploymentService
from backend.src.domain.ports.services.weekly_project_summarization.i_weekly_commits_summarizer import IWeeklyCommitsSummarizer
from backend.src.domain.ports.services.weekly_project_summarization.i_weekly_deployments_summarizer import IWeeklyDeploymentsSummarizer


logger = logging.getLogger(__name__)


class SummarizeWeeklyProjectUseCase(ISummarizeWeeklyProjectUseCase):
    """
    Application use case for generating a weekly project activity summary.

    This use case orchestrates the aggregation of ClickUp, GitHub commits,
    and GitHub deployments to produce a structured weekly report including
    both raw data and LLM-generated summaries.

    Attributes:
        _clickup_reader (IClickUpReader): Port used to retrieve ClickUp workspace structure and tasks.
        _weekly_commits_summarizer (IWeeklyCommitsSummarizer): Service responsible for generating commit summaries.
        _weekly_deployments_summarizer (IWeeklyDeploymentsSummarizer): Service responsible for generating deployment summaries.
        _github_commit_service (IGitHubCommitService): Service used to fetch GitHub commit history.
        _github_deployment_service (IGitHubDeploymentService): Service used to fetch GitHub deployment history.
    """

    def __init__(
        self,
        clickup_reader: IClickUpReader,
        weekly_commits_summarizer: IWeeklyCommitsSummarizer,
        weekly_deployments_summarizer: IWeeklyDeploymentsSummarizer,
        github_deployment_service: IGitHubDeploymentService,
        github_commit_service: IGitHubCommitService,
    ):
        """
        Initialize the SummarizeWeeklyProjectUseCase.

        Args:
            clickup_reader: ClickUp reader port implementation used to retrieve workspace structure.
            weekly_commits_summarizer: Service responsible for summarizing GitHub commits.
            weekly_deployments_summarizer: Service responsible for summarizing GitHub deployments.
            github_deployment_service: Service used to fetch GitHub deployment data.
            github_commit_service: Service used to fetch GitHub commit data.
        """
        self._clickup_reader = clickup_reader
        self._weekly_commits_summarizer = weekly_commits_summarizer
        self._weekly_deployments_summarizer = weekly_deployments_summarizer
        self._github_commit_service = github_commit_service
        self._github_deployment_service = github_deployment_service

    async def get_weekly_project_summary(self, space_id: str, repo_url: Optional[str]) -> WeeklyProjectSummaryResponse:
        """
        Generate a weekly project summary.

        This method:
        - Retrieves all ClickUp tasks for the given space
        - Classifies task activity over the last 7 days
        - Fetches GitHub commits and deployments (if repository exists)
        - Generates AI-based summaries for commits and deployments
        - Returns a structured weekly report

        Args:
            space_id: Identifier of the ClickUp space to analyze.
            repo_url: Optional GitHub repository URL linked to the project.

        Returns:
            WeeklyProjectSummaryResponse: Structured weekly report including
                task activity, commits, deployments, and AI-generated summaries.
        """
        logger.info("Fetching weekly project summary. space_id=%s.", space_id)

        folder_with_tasks = self._clickup_reader.get_space_full_structure(space_id)

        tasks =[
            task
            for folder in folder_with_tasks
            for lst in folder.lists
            for task in lst.tasks
        ]

        if not tasks and not repo_url:
            return WeeklyProjectSummaryResponse(
                status=WeeklyProjectSummaryStatus.NO_GITHUB_AND_CLICKUP_EMPTY,
                message=(
                    "The project has no ClickUp tasks and is not linked to any GitHub repository yet. "
                    "No weekly project activity is currently available."
                ),
                created_tasks=[],
                in_progress_tasks=[],
                done_tasks=[],
                last_7_days_deployments=[],
                deployments_summary="",
                last_7_days_commits=[],
                commits_summary="",
            )

        results = await asyncio.gather(*[fetch_task_context(task, self._clickup_reader) for task in tasks])

        tasks_created: List[ClickUpTask] = []
        tasks_to_done: List[ClickUpTask] = []
        task_to_in_progress: List[ClickUpTask] = []

        now = datetime.datetime.now(tz=datetime.timezone.utc)
        since = now - datetime.timedelta(days=7)

        for task, task_context in results:
            date_created: Optional[datetime.datetime] = task_context.get("date_created")
            date_closed: Optional[datetime.datetime] = task_context.get("date_closed")
            since_current_status: Optional[datetime.datetime] = task_context.get("since_current_status")

            if date_created and date_created >= since:
                tasks_created.append(task)

            if date_closed and date_closed >= since:
                tasks_to_done.append(task)

            if task.status.lower() in ("in progress", "in_progress") and since_current_status and since_current_status >= since:
                task_to_in_progress.append(task)

        last_7_days_deployments: List[DeploymentDTO] = []
        deployments_summary = ""
        last_7_days_commits: List[CommitDTO] = []
        commits_summary = ""

        if repo_url:
            last_7_days_deployments = await self._github_deployment_service.get_deployments_between_dates(
                repo_url,
                since=since,
                until=now,
                max_deployments=20,
            )

            if last_7_days_deployments:
                deployments_summary = self._weekly_deployments_summarizer.summarize_deployments(last_7_days_deployments)

            last_7_days_commits = await self._github_commit_service.get_commits_between_dates(
                repo_url,
                since=since,
                until=now,
                max_commits=70,
            )

            if last_7_days_commits:
                commits_summary = self._weekly_commits_summarizer.summarize_commits(last_7_days_commits)

        logger.info(
            "Weekly project summary computation completed successfully: space_id=%s tasks=%d.",
            space_id,
            len(tasks),
        )

        if not tasks:
            status = WeeklyProjectSummaryStatus.CLICKUP_EMPTY
            message = (
                "The ClickUp workspace does not contain any tasks yet. "
                "The weekly summary is currently based only on the linked GitHub activity."
            )

        elif not repo_url:
            status = WeeklyProjectSummaryStatus.NO_GITHUB
            message = (
                "This project is not linked to any GitHub repository. "
                "The weekly summary below is based solely on ClickUp task activity."
            )

        else:
            status = WeeklyProjectSummaryStatus.FULL
            message = (
                "The weekly summary was successfully generated using both ClickUp activity "
                "and GitHub commit and deployment data."
            )

        return WeeklyProjectSummaryResponse(
            status=status,
            message=message,
            created_tasks=tasks_created,
            in_progress_tasks=task_to_in_progress,
            done_tasks=tasks_to_done,
            last_7_days_deployments=last_7_days_deployments,
            deployments_summary=deployments_summary,
            last_7_days_commits=last_7_days_commits,
            commits_summary=commits_summary,
        )
