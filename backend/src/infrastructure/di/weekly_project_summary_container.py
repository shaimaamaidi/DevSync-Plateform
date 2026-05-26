"""
Dependency container for weekly project summary workflow.

This module defines the WeeklyProjectSummaryContainer class, which wires together
AI agents, ClickUp infrastructure, GitHub services, and application use cases
required for weekly project summarization workflows.

It is responsible for initializing all components required for:
- Weekly commit analysis and summarization
- Weekly deployment analysis and summarization
- Aggregation of ClickUp tasks with GitHub activity
- Generation of a unified weekly project summary view
- Orchestration of weekly project health reporting

Classes:
    WeeklyProjectSummaryContainer: Application-scoped dependency injection container.
"""

import logging

from backend.src.application.use_cases.summarize_weekly_project_use_case import SummarizeWeeklyProjectUseCase

from backend.src.domain.exceptions.base.app_exception import AppException
from backend.src.infrastructure.di.bas_ai_container import BaseAIContainer

from backend.src.infrastructure.di.base_clickup_container import BaseClickUpContainer
from backend.src.infrastructure.di.base_github_container import BaseGitHubContainer

from backend.src.infrastructure.external.weekly_project_summary.weekly_commits_summarizer_agent import WeeklyCommitsSummarizerAgent
from backend.src.infrastructure.external.weekly_project_summary.weekly_deployments_summarizer_agent import WeeklyDeploymentsSummarizerAgent


logger = logging.getLogger(__name__)


class WeeklyProjectSummaryContainer(BaseAIContainer, BaseClickUpContainer, BaseGitHubContainer):
    """
    Dependency injection container for weekly project summary workflow.

    This container orchestrates all dependencies required for generating
    weekly project summaries.

    It is responsible for:
    - Initializing AI prompt-based agents (commits & deployments summarizers)
    - Initializing ClickUp infrastructure (via base container)
    - Initializing GitHub services (commits & deployments)
    - Wiring application use case for weekly project summary
    - Providing a fully configured summarization use case for execution layer

    Attributes:
        github_deployment_service (GitHubDeploymentAdapter):
            Service responsible for retrieving GitHub deployment data.
        github_commit_service (GitHubCommitsAdapter):
            Service responsible for retrieving GitHub commit history.

        commits_summarizer_agent (WeeklyCommitsSummarizerAgent):
            LLM-based agent for summarizing weekly commits.
        deployments_summarizer_agent (WeeklyDeploymentsSummarizerAgent):
            LLM-based agent for summarizing weekly deployments.

        weekly_project_summarizer_use_case (SummarizeWeeklyProjectUseCase):
            Application use case for generating weekly project summaries.
    """

    def __init__(self):
        """
        Initialize the WeeklyProjectSummaryContainer.

        This constructor initializes all required infrastructure and agents:
        - AI prompt system (BaseAIContainer)
        - ClickUp infrastructure (BaseClickUpContainer)
        - GitHub infrastructure (BaseGitHubContainer)
        - GitHub commit/deployment services
        - Weekly summarization LLM agents
        - Weekly project summary application use case

        Raises:
            AppException: If any dependency initialization fails.
        """
        logger.info("Initializing weekly project summary container.")

        try:
            BaseAIContainer.__init__(self)
            BaseClickUpContainer.__init__(self)
            BaseGitHubContainer.__init__(self)
            self._init_weekly_project_summary_agents()
            self._init_weekly_project_summary_use_cases()

            logger.info("Weekly project summary container initialized successfully.")

        except AppException:
            raise
        except Exception as e:
            logger.exception("Failed to initialize weekly project summary container.")
            raise AppException(
                "Weekly project summary services are currently unavailable. Please try again later.",
                "TASK_STATUS_CONTAINER_INIT_ERROR",
                http_status=500,
            ) from e

    def _init_weekly_project_summary_agents(self):
        """
        Initialize LLM-based weekly project summary agents.

        These agents are responsible for:
        - Summarizing weekly GitHub commits
        - Summarizing weekly GitHub deployments
        """
        logger.info("Initializing weekly project summary agents.")

        self.deployments_summarizer_agent = WeeklyDeploymentsSummarizerAgent(self.prompt_loader)
        self.commits_summarizer_agent = WeeklyCommitsSummarizerAgent(self.prompt_loader)

    def _init_weekly_project_summary_use_cases(self):
        """
        Initialize weekly project summary application use case.

        This method wires together:
        - ClickUp infrastructure (reader)
        - LLM summarization agents (commits & deployments)
        - GitHub services (commits & deployments)

        into a fully functional weekly project summarization pipeline.
        """
        logger.info("Initializing weekly project summary use case.")

        self.weekly_project_summarizer_use_case = SummarizeWeeklyProjectUseCase(
            self.clickup_reader,
            self.commits_summarizer_agent,
            self.deployments_summarizer_agent,
            self.github_deployment_service,
            self.github_commit_service,
        )