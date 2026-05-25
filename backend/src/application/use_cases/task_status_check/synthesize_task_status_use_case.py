"""
Task status synthesis use case module.

This module provides the SynthesizeTaskStatusUseCase class, which is responsible for
orchestrating the analysis and synthesis of ClickUp task status.

It coordinates retrieval of external GitHub context (commits and deployments),
delegates synthesis logic to a domain service, and returns a structured
task status result enriched with LLM-based analysis.

Classes:
    SynthesizeTaskStatusUseCase: Main use case for synthesizing task status.
"""

import logging
import asyncio
from typing import Optional
from datetime import datetime, timezone, timedelta

from backend.src.domain.entities.check_task_status.synthesized_task_status_result import SynthesizedTaskStatusResult
from backend.src.domain.entities.clickup.list_with_tasks import ClickUpTask
from backend.src.domain.ports.input.task_status_check.i_synthesize_task_status_use_case import ISynthesizeTaskStatusUseCase
from backend.src.domain.ports.output.clickup.i_clickup_reader import IClickUpReader
from backend.src.domain.ports.output.github.i_github_commit_service import IGitHubCommitService
from backend.src.domain.ports.output.github.i_github_deployment_service import IGitHubDeploymentService
from backend.src.domain.ports.services.task_status_check.i_task_status_synthesizer import ITaskStatusSynthesizer


logger = logging.getLogger(__name__)


class SynthesizeTaskStatusUseCase(ISynthesizeTaskStatusUseCase):
    """
    Application use case for synthesizing ClickUp task status.

    This use case orchestrates the full task status analysis flow by:
    - Fetching GitHub deployments linked to a repository (if provided)
    - Fetching GitHub commits linked to a repository (if provided)
    - Delegating synthesis logic to a task status synthesizer service
    - Returning a structured result representing task completion state

    Attributes:
        _task_status_analyzer (ITaskStatusSynthesizer): Service responsible for synthesizing task status.
        _github_deployment_service (IGitHubDeploymentService): Service to fetch deployment data from GitHub.
        _github_commit_service (IGitHubCommitService): Service to fetch commit history from GitHub.
        _clickup_reader (IClickUpReader): Port used to fetch data from ClickUp API.
    """

    _MAX_COMMITS_TODO = 30
    _MAX_COMMITS_IN_PROGRESS = 60
    _MAX_COMMITS_DONE = 60

    _MAX_DEPLOYMENTS_TODO = 5
    _MAX_DEPLOYMENTS_IN_PROGRESS = 10
    _MAX_DEPLOYMENTS_DONE = 15

    _TODO_LOOKBACK_DAYS = 30
    _TODO_LIGHT_DAYS = 7
    _IN_PROGRESS_BUFFER_DAYS = 2
    _DONE_BUFFER_DAYS = 3
    
    def __init__(
        self,
        task_status_analyzer: ITaskStatusSynthesizer,
        github_deployment_service: IGitHubDeploymentService,
        github_commit_service: IGitHubCommitService,
        clickup_reader: IClickUpReader
    ):
        """
        Initialize the SynthesizeTaskStatusUseCase.

        Args:
            task_status_analyzer: Service responsible for synthesizing task status.
            github_deployment_service: Service used to retrieve deployment data from GitHub.
            github_commit_service: Service used to retrieve commit history from GitHub.
            clickup_reader: ClickUp reader port implementation used to retrieve workspace data.
        """
        self._task_status_analyzer = task_status_analyzer
        self._github_deployment_service = github_deployment_service
        self._github_commit_service = github_commit_service
        self._clickup_reader = clickup_reader

    async def analyze_task_status(self, repo_url: Optional[str], task: ClickUpTask) -> SynthesizedTaskStatusResult:
        """
        Analyze and synthesize the status of a ClickUp task.

        This method:
        - Retrieves GitHub deployments and commits if a repository URL is provided
        - Sends task + external context to the synthesizer service
        - Returns a structured synthesis result indicating completion status

        Args:
            repo_url: Optional GitHub repository URL associated with the task.
            task: ClickUp task to analyze.

        Returns:
            SynthesizedTaskStatusResult: Synthesized result containing:
                - Completion status
                - Confidence level
                - Summary explanation
                - Supporting evidence
        """
        logger.info(
            "Synthesize task in ClickUp: task_id=%s.",
            task.id,
        )

        time_context = self._clickup_reader.get_task_time_context(task.id)

        since, until, max_commits, max_deployments = SynthesizeTaskStatusUseCase._compute_window(task, time_context)

        deployments = []
        commits = []

        if repo_url and since is not None:
            commits, deployments = await self._fetch_github_context(
                repo_url=repo_url,
                since=since,
                until=until,
                max_commits=max_commits,
                max_deployments=max_deployments
            )

            logger.info(
                "GitHub context fetched. task_id=%s commits=%d deployments=%d.",
                task.id, len(commits), len(deployments),
            )

        signals = SynthesizeTaskStatusUseCase._derive_signals(time_context, commits, deployments)

        result =  self._task_status_analyzer.synthesize_task_status(task, deployments, commits, signals)

        logger.info(
            "Task synthesize completed successfully: task_id=%s status_result=%d.",
            task.id,
            result.is_completed,
        )

        return result

    @staticmethod
    def _compute_window(task: ClickUpTask, time_context: dict) -> tuple[datetime | None, datetime, int, int]:
        """
        Compute the [since, until] fetch window and commit cap from task date signals.

        Strategy per status:

            Todo
                Light fetch: max(since_current_status, today-30d) → today, cap 30.
                Returns since=None if since_current_status is unavailable AND
                task was created more than 30 days ago (confirmed inactive → skip fetch).

            In Progress
                since_current_status - 2d buffer → today, cap 60.
                Falls back to date_created if since_current_status is unavailable.

            Done
                date_created → date_closed + 3d buffer, cap 60.
                Falls back to today if date_closed is missing.

            Unknown / other
                Fallback: today-30d → today, cap 60.

        Args:
            time_context: Dict returned by get_task_time_context().

        Returns:
            Tuple (since, until, max_commits).
            since=None signals "skip GitHub fetch entirely".
        """
        now = datetime.now(tz=timezone.utc)

        status = task.status.lower()

        date_created = time_context.get("date_created")
        date_closed = time_context.get("date_closed")
        since_current_status = time_context.get("since_current_status")

        if status == "todo":
            fallback_since = now - timedelta(days=SynthesizeTaskStatusUseCase._TODO_LOOKBACK_DAYS)
            anchor = since_current_status or date_created or fallback_since

            if (now - anchor).days > SynthesizeTaskStatusUseCase._TODO_LOOKBACK_DAYS:
                logger.info(
                    "Todo task inactive for >%d days — skipping GitHub fetch.",
                    SynthesizeTaskStatusUseCase._TODO_LOOKBACK_DAYS,
                )
                return None, now, SynthesizeTaskStatusUseCase._MAX_COMMITS_TODO, SynthesizeTaskStatusUseCase._MAX_DEPLOYMENTS_TODO

            since = max(anchor, fallback_since)
            return since, now, SynthesizeTaskStatusUseCase._MAX_COMMITS_TODO, SynthesizeTaskStatusUseCase._MAX_DEPLOYMENTS_TODO

        if "progress" in status or status == "in progress":
            anchor = since_current_status or date_created or (now - timedelta(days=SynthesizeTaskStatusUseCase._TODO_LOOKBACK_DAYS))
            since = anchor - timedelta(days=SynthesizeTaskStatusUseCase._IN_PROGRESS_BUFFER_DAYS)
            return since, now, SynthesizeTaskStatusUseCase._MAX_COMMITS_IN_PROGRESS, SynthesizeTaskStatusUseCase._MAX_DEPLOYMENTS_IN_PROGRESS

        if status in ("done", "closed", "complete", "completed"):
            since = date_created or (now - timedelta(days=SynthesizeTaskStatusUseCase._TODO_LOOKBACK_DAYS))
            until = (date_closed or now) + timedelta(days=SynthesizeTaskStatusUseCase._DONE_BUFFER_DAYS)
            until = min(until, now)
            return since, until, SynthesizeTaskStatusUseCase._MAX_COMMITS_DONE, SynthesizeTaskStatusUseCase._MAX_DEPLOYMENTS_DONE

        logger.warning(
            "Unrecognised status '%s' — using 30-day fallback window.", status
        )

        return now - timedelta(days=SynthesizeTaskStatusUseCase._TODO_LOOKBACK_DAYS), now, SynthesizeTaskStatusUseCase._MAX_COMMITS_DONE, SynthesizeTaskStatusUseCase._MAX_DEPLOYMENTS_TODO

    async def _fetch_github_context(
            self,
            repo_url: str,
            since: datetime,
            until: datetime,
            max_commits: int,
            max_deployments:int,
    ) -> tuple[list, list]:
        """
        Fetch commits and deployments within [since, until] in parallel.

        Args:
            repo_url: GitHub repository URL.
            since: Window start (inclusive).
            until: Window end (inclusive).
            max_commits: Commit cap to pass to the commit service.
            max_deployments: Deployment cap to pass to the deployment service.

        Returns:
            Tuple (commits, deployments).
        """
        commits_coro = self._github_commit_service.get_commits_between_dates(
            repo_url, since, until, max_commits
        )
        deployments_coro = self._github_deployment_service.get_deployments_between_dates(
            repo_url, since, until, max_deployments
        )

        commits, deployments = await asyncio.gather(commits_coro, deployments_coro)
        return commits, deployments

    @staticmethod
    def _derive_signals(
            time_context: dict,
            commits: list,
            deployments: list,
    ) -> dict:
        """
        Derive human-readable signals from raw time context and GitHub data.
        These signals are passed to the LLM instead of raw datetime objects.

        Returns:
            Dict with interpreted signals ready for LLM consumption.
        """
        now = datetime.now(tz=timezone.utc)

        date_created = time_context.get("date_created")
        date_closed = time_context.get("date_closed")
        since_current_status = time_context.get("since_current_status")

        anchor = since_current_status or date_created
        days_in_current_status = (now - anchor).days if anchor else None

        commits_after_close = []
        if date_closed and commits:
            commits_after_close = [
                c for c in commits
                if c.date and c.date > date_closed
            ]

        latest_commit_days_ago = None
        if commits:
            latest = max((c.date for c in commits if c.date), default=None)
            if latest:
                latest_commit_days_ago = (now - latest).days

        deployed_to_prod_after_close = any(
            d for d in deployments
            if "prod" in (d.environment or "").lower()
            and d.state == "success"
            and (date_closed is None or (d.created_at and d.created_at >= date_closed))
        )

        return {
            "days_in_current_status": days_in_current_status,
            "commits_after_close_count": len(commits_after_close),
            "commits_after_close": [c.message for c in commits_after_close],
            "latest_commit_days_ago": latest_commit_days_ago,
            "deployed_to_prod_after_close": deployed_to_prod_after_close,
            "has_any_commit": len(commits) > 0,
            "has_any_deployment": len(deployments) > 0,
        }