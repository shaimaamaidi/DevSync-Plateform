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
from typing import Optional

from backend.src.domain.entities.check_task_status.synthesized_task_status_result import SynthesizedTaskStatusResult
from backend.src.domain.entities.clickup.list_with_tasks import ClickUpTask
from backend.src.domain.ports.input.task_status_check.i_synthesize_task_status_use_case import ISynthesizeTaskStatusUseCase
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
    """

    def __init__(
        self,
        task_status_analyzer: ITaskStatusSynthesizer,
        github_deployment_service: IGitHubDeploymentService,
        github_commit_service: IGitHubCommitService
    ):
        """
        Initialize the SynthesizeTaskStatusUseCase.

        Args:
            task_status_analyzer: Service responsible for synthesizing task status.
            github_deployment_service: Service used to retrieve deployment data from GitHub.
            github_commit_service: Service used to retrieve commit history from GitHub.
        """
        self._task_status_analyzer = task_status_analyzer
        self._github_deployment_service = github_deployment_service
        self._github_commit_service = github_commit_service


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

        deployments = []
        commits = []

        if repo_url:
            deployments = await self._github_deployment_service.get_deployments(repo_url, max_deployments=10)
            commits = await self._github_commit_service.get_commits(repo_url, max_commits=25)


        result =  self._task_status_analyzer.synthesize_task_status(task, deployments, commits)

        logger.info(
            "Task synthesize completed successfully: task_id=%s status_result=%d.",
            task.id,
            result.is_completed,
        )

        return result