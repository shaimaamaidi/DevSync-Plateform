"""
Dependency container for task status workflow.

This module defines the TaskStatusContainer class, which wires together
AI agents, ClickUp infrastructure, GitHub services, and application use
cases required for task status search and synthesis workflows.

It is responsible for initializing all components required for:
- Task search within ClickUp spaces using LLM-based agents
- Task status synthesis using GitHub commits and deployments
- Integration between ClickUp, GitHub, and AI prompt services
- Orchestration of task status evaluation workflows

Classes:
    TaskStatusContainer: Application-scoped dependency injection container.
"""

import logging

from backend.src.application.use_cases.task_status_check.search_task_use_case import SearchTaskUseCase
from backend.src.application.use_cases.task_status_check.synthesize_task_status_use_case import SynthesizeTaskStatusUseCase

from backend.src.domain.exceptions.base.app_exception import AppException
from backend.src.infrastructure.di.bas_ai_container import BaseAIContainer

from backend.src.infrastructure.di.base_clickup_container import BaseClickUpContainer
from backend.src.infrastructure.di.base_github_container import BaseGitHubContainer

from backend.src.infrastructure.external.github.github_deployments import GitHubDeploymentAdapter
from backend.src.infrastructure.external.github.github_commits import GitHubCommitsAdapter
from backend.src.infrastructure.external.task_status_check.task_search_agent import TaskSearchAgent
from backend.src.infrastructure.external.task_status_check.task_status_synthesizer_agent import TaskStatusSynthesizerAgent


logger = logging.getLogger(__name__)


class TaskStatusContainer(BaseAIContainer, BaseClickUpContainer, BaseGitHubContainer):
    """
    Dependency injection container for task status workflow.

    This container orchestrates all dependencies required for task status
    analysis and search operations.

    It is responsible for:
    - Initializing AI prompt-based agents (task search & synthesis)
    - Initializing ClickUp infrastructure (via base container)
    - Initializing GitHub services (commits & deployments)
    - Wiring application use cases for task status workflows
    - Providing fully configured use cases for execution layer

    Attributes:
        github_deployment_service (GitHubDeploymentAdapter):
            Service responsible for retrieving GitHub deployment data.
        github_commit_service (GitHubCommitsAdapter):
            Service responsible for retrieving GitHub commit history.

        task_search_agent (TaskSearchAgent):
            LLM-based agent for semantic task search.
        task_status_synthesizer_agent (TaskStatusSynthesizerAgent):
            LLM-based agent for task status synthesis.

        task_search_use_case (SearchTaskUseCase):
            Application use case for searching tasks.
        task_status_synthesize_use_case (SynthesizeTaskStatusUseCase):
            Application use case for synthesizing task status.
    """

    def __init__(self):
        """
        Initialize the TaskStatusContainer.

        This constructor initializes all required infrastructure and agents:
        - AI prompt system (BaseAIContainer)
        - ClickUp infrastructure (BaseClickUpContainer)
        - GitHub infrastructure (BaseGitHubContainer)
        - GitHub commit/deployment services
        - Task status LLM agents
        - Task status application use cases

        Raises:
            AppException: If any dependency initialization fails.
        """
        logger.info("Initializing task status container.")

        try:
            BaseAIContainer.__init__(self)
            BaseClickUpContainer.__init__(self)
            BaseGitHubContainer.__init__(self)
            self._init_github_commit_service()
            self._init_task_status_agents()
            self._init_task_status_use_cases()

            logger.info("Task status container initialized successfully.")

        except AppException:
            raise
        except Exception as e:
            logger.exception("Failed to initialize task status container.")
            raise AppException(
                "Task status services are currently unavailable. Please try again later.",
                "TASK_STATUS_CONTAINER_INIT_ERROR",
                http_status=500,
            ) from e

    def _init_github_commit_service(self):
        """
        Initialize GitHub commit service.

        This service is responsible for retrieving commit history
        associated with repositories for task status synthesis.
        """
        logger.info("Initializing GitHub commit service.")
        try:
            self.github_commit_service = GitHubCommitsAdapter()
        except Exception as e:
            logger.exception("Failed to initialize GitHubCommitsAdapter.")
            raise AppException(
                "GitHub services are currently unavailable. Please try again later.",
                "GITHUB_ADAPTER_INIT_ERROR",
                http_status=500,
            ) from e

    def _init_github_services(self):
        """
        Initialize GitHub adapter services for deployments and commits.
        """
        logger.info("Initializing GitHub services.")

        self.github_commit_service = GitHubCommitsAdapter()

    def _init_task_status_agents(self):
        """
        Initialize LLM-based task status agents.

        These agents are responsible for:
        - Semantic task search within ClickUp
        - Task status synthesis using external context
        """
        logger.info("Initializing task status agents.")

        self.task_search_agent = TaskSearchAgent(self.prompt_loader)
        self.task_status_synthesizer_agent = TaskStatusSynthesizerAgent(self.prompt_loader)

    def _init_task_status_use_cases(self):
        """
        Initialize task status application use cases.

        This method wires together:
        - ClickUp infrastructure (reader)
        - LLM agents (search & synthesis)
        - GitHub services (commits & deployments)

        into fully functional application use cases.
        """
        logger.info("Initializing task status use cases.")

        self.task_search_use_case = SearchTaskUseCase(
            self.clickup_reader,
            self.task_search_agent,
        )
        self.task_status_synthesize_use_case = SynthesizeTaskStatusUseCase(
            self.task_status_synthesizer_agent,
            self.github_deployment_service,
            self.github_commit_service,
        )