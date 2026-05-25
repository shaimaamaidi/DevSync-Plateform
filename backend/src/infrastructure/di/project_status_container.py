"""
Dependency container for project status workflow.

This module defines the ProjectStatusContainer class, which acts as a composition root
responsible for wiring all dependencies required for project status evaluation.

It initializes and connects infrastructure, AI agents, and application use cases
used to compute a unified view of project health and activity.

The container integrates:
- ClickUp data access layer (task retrieval and workspace structure)
- GitHub services (commits and deployments)
- AI-based analysis agents (stale tasks and unverified completed tasks)
- Application use cases for project status computation

It ensures that all dependencies are properly instantiated and injected
before being used by the application layer.

Classes:
    ProjectStatusContainer: Application-scoped dependency injection container.
"""

import logging

from backend.src.application.use_cases.check_project_status_use_case import CheckProjectStatusUseCase

from backend.src.domain.exceptions.base.app_exception import AppException
from backend.src.infrastructure.di.bas_ai_container import BaseAIContainer

from backend.src.infrastructure.di.base_clickup_container import BaseClickUpContainer
from backend.src.infrastructure.di.base_github_container import BaseGitHubContainer

from backend.src.infrastructure.external.project_status_check.stale_task_inspector_agent import StaleTaskInspectorAgent
from backend.src.infrastructure.external.project_status_check.unverified_done_task_inspector_agent import \
    UnverifiedDoneTaskInspectorAgent

logger = logging.getLogger(__name__)


class ProjectStatusContainer(BaseAIContainer, BaseClickUpContainer, BaseGitHubContainer):
    """
    Dependency injection container for project status workflow.

    This container orchestrates all dependencies required for project status
    evaluation and analysis operations.

    It is responsible for:
    - Initializing AI prompt-based agents (stale task inspection)
    - Initializing ClickUp infrastructure (via base container)
    - Initializing GitHub services (commits & deployments)
    - Wiring application use cases for project status computation
    - Providing fully configured use cases for execution layer

    Attributes:
        github_deployment_service (GitHubDeploymentAdapter):
            Service responsible for retrieving GitHub deployment data.
        github_commit_service (GitHubCommitsAdapter):
            Service responsible for retrieving GitHub commit history.

        stale_task_inspector_agent (StaleTaskInspectorAgent):
            LLM-based agent for detecting stale in-progress tasks.

        unverified_done_task_inspector_agent:
            Validates completed tasks against GitHub activity.

        project_status_check_use_case (CheckProjectStatusUseCase):
            Application use case for computing project status.
    """

    def __init__(self):
        """
        Initialize the ProjectStatusContainer.

        This constructor initializes all required infrastructure and agents:
        - AI prompt system (BaseAIContainer)
        - ClickUp infrastructure (BaseClickUpContainer)
        - GitHub infrastructure (BaseGitHubContainer)
        - GitHub commit/deployment services
        - Stale task inspection LLM agent
        - Project status application use case

        Raises:
            AppException: If any dependency initialization fails.
        """
        logger.info("Initializing project status container.")

        try:
            BaseAIContainer.__init__(self)
            BaseClickUpContainer.__init__(self)
            BaseGitHubContainer.__init__(self)
            self._init_stale_task_inspector_agent()
            self._init_unverified_done_task_inspector_agent()
            self._init_project_status_check_use_cases()

            logger.info("Project status container initialized successfully.")

        except AppException:
            raise
        except Exception as e:
            logger.exception("Failed to initialize project status container.")
            raise AppException(
                "Project status checking service are currently unavailable. Please try again later.",
                "PROJECT_STATUS_CONTAINER_INIT_ERROR",
                http_status=500,
            ) from e

    def _init_stale_task_inspector_agent(self):
        """
        Initialize LLM-based stale task inspector agent.

        This agent is responsible for analyzing in-progress ClickUp tasks
        and detecting whether they are stale based on GitHub commit activity.
        """
        logger.info("Initializing stale task inspector agent.")

        self.stale_task_inspector_agent = StaleTaskInspectorAgent(self.prompt_loader)

    def _init_unverified_done_task_inspector_agent(self):
        """
        Initialize LLM-based unverified done task inspector agent.

        This agent is responsible for analyzing recently completed ClickUp tasks
        and verifying whether each task has a semantically related GitHub commit
        as evidence that the work was actually performed.
        """
        logger.info("Initializing unverified done task inspector agent.")

        self.unverified_done_task_inspector_agent = UnverifiedDoneTaskInspectorAgent(self.prompt_loader)

    def _init_project_status_check_use_cases(self):
        """
        Initialize project status application use cases.

        This method wires together:
        - ClickUp infrastructure (reader)
        - GitHub services (commits & deployments)
        - AI agents (stale task inspection & unverified done task inspection)

        into a fully functional project status use case.
        """
        logger.info("Initializing project status checking use cases.")

        self.project_status_check_use_case = CheckProjectStatusUseCase(
            self.clickup_reader,
            self.stale_task_inspector_agent,
            self.unverified_done_task_inspector_agent,
            self.github_deployment_service,
            self.github_commit_service,
        )

