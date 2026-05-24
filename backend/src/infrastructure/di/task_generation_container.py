"""
Dependency container for backlog generation workflow.

This module defines the TaskGenerationContainer class, which wires together
LLM agents, external adapters, and application use cases required for
backlog generation and task verification workflows.

It is responsible for initializing all components required for:
- Task generation from summaries and backlog inputs
- Task verification using LLM-based agents
- ClickUp integration (read/write operations)
- Prompt-based AI services
- Workflow orchestration and factory use cases

Classes:
    TaskGenerationContainer: Request/application-scoped dependency injection container.
"""

import logging

from backend.src.application.use_cases.generate_tasks_from_backlog_use_case import GenerateTasksFromBacklogUseCase
from backend.src.application.use_cases.generate_tasks_from_summary_use_case import GenerateTasksFromSummaryUseCase
from backend.src.application.use_cases.save_backlog_tasks_use_case import SaveBacklogTasksInClickUpUseCase
from backend.src.application.use_cases.save_summary_tasks_use_case import SaveSummaryTasksInClickUpUseCase
from backend.src.application.use_cases.verify_tasks_from_backlog_use_case import VerifyTasksFromBacklogUseCase
from backend.src.application.use_cases.verify_tasks_from_summary_use_case import VerifyTasksFromSummaryUseCase

from backend.src.domain.exceptions.base.app_exception import AppException
from backend.src.domain.exceptions.system.service_unavailable_exception import ServiceUnavailableException
from backend.src.domain.ports.repositories.i_member_repository import IMemberRepository
from backend.src.infrastructure.di.bas_ai_container import BaseAIContainer
from backend.src.infrastructure.di.base_clickup_container import BaseClickUpContainer

from backend.src.infrastructure.external.clickup.clickup_reader import ClickUpReader
from backend.src.infrastructure.external.clickup.writer.clickup_task_writer import ClickUpTaskWriter
from backend.src.infrastructure.external.clickup.client.clickup_http_client import ClickUpHttpClient
from backend.src.infrastructure.external.task_verification.task_from_backlog_verifier_agent import \
    TaskFromBacklogVerifierAgent
from backend.src.infrastructure.external.task_verification.task_from_summary_verifier_agent import \
    TaskFromSummaryVerifierAgent
from backend.src.infrastructure.external.task_generation_from_backlog.clickup_task_generator_from_backlog_agent import \
    ClickUpTaskGeneratorFromBacklogAgent
from backend.src.infrastructure.external.task_generation_from_summary.clickup_task_generator_from_summary_agent import \
    ClickUpTaskFromSummaryGeneratorAgent


logger = logging.getLogger(__name__)


class TaskGenerationContainer(BaseAIContainer, BaseClickUpContainer):
    """
    Dependency injection container for backlog generation workflow.

    This container orchestrates all dependencies required for AI-powered
    backlog generation and task verification workflows.

    It is responsible for:
    - Initializing AI prompt-based agents (LLM task generation & verification)
    - Initializing ClickUp infrastructure (reader, writer)
    - Wiring application use cases for task generation and persistence
    - Providing factory methods for request-scoped workflow execution
    - Ensuring safe initialization of all required services

    Attributes:
        clickup_writer (ClickUpTaskWriter | None):
            Service responsible for writing tasks to ClickUp.
        http_client (ClickUpHttpClient):
            HTTP client used for ClickUp API communication.
        clickup_reader (ClickUpReader):
            Service responsible for reading ClickUp workspace data.

        clickup_task_generator_from_summary_use_case (GenerateTasksFromSummaryUseCase | None):
            Use case for generating ClickUp tasks from summary inputs.
        clickup_task_generator_from_backlog_use_case (GenerateTasksFromBacklogUseCase | None):
            Use case for generating ClickUp tasks from backlog inputs.
    """

    def __init__(self):
        """
        Initialize the TaskGenerationContainer.

        This constructor initializes:
        - AI prompt loader (via BaseAIContainer)
        - ClickUp infrastructure (via BaseClickUpContainer)
        - Task generation agents and verification agents
        - Workflow use cases for backlog and summary processing

        Raises:
            AppException: If any required dependency fails to initialize.
        """
        logger.info("Initializing task generation container.")

        self.clickup_task_generator_from_summary_use_case: GenerateTasksFromSummaryUseCase | None = None
        self.clickup_task_generator_from_backlog_use_case: GenerateTasksFromBacklogUseCase | None = None

        try:
            BaseAIContainer.__init__(self)
            BaseClickUpContainer.__init__(self)
            self._init_tasks_generation_from_summary()
            self._init_tasks_verification_agent()

            logger.info("Task generation container initialized successfully.")

        except AppException:
            raise
        except Exception as e:
            logger.exception("Failed to initialize task generation container.")
            raise AppException(
                "Task generation services are currently unavailable. Please try again later.",
                "TASK_GENERATION_CONTAINER_INIT_ERROR",
                http_status=500,
            ) from e

    def _init_tasks_generation_from_summary(self):
        """
        Initialize task generation from summary workflow.

        This sets up:
        - LLM-based task generator agent (summary-based)
        - Use case for generating ClickUp tasks from summaries
        """
        logger.info("Initializing task generation from summary use case.")

        self.clickup_task_generator_from_summary_agent = ClickUpTaskFromSummaryGeneratorAgent(self.prompt_loader)
        self.clickup_task_generator_from_summary_use_case = GenerateTasksFromSummaryUseCase(
            self.clickup_reader,
            self.clickup_task_generator_from_summary_agent,
        )

    def _init_tasks_generation_from_backlog(self):
        """
        Initialize task generation from backlog workflow.

        This sets up:
        - LLM-based task generator agent (backlog-based)
        - Use case for generating ClickUp tasks from backlog inputs
        """
        logger.info("Initializing task generation from backlog use case.")

        self.clickup_task_generator_from_backlog_agent = ClickUpTaskGeneratorFromBacklogAgent(self.prompt_loader)
        self.clickup_task_generator_from_backlog_use_case = GenerateTasksFromBacklogUseCase(
            self.clickup_reader,
            self.clickup_task_generator_from_backlog_agent,
        )

    def _init_tasks_verification_agent(self):
        """
        Initialize task verification agents.

        This method sets up LLM-based verification agents used to validate
        generated tasks before persistence into ClickUp.
        """
        logger.info("Initializing task verification agent.")

        self.task_from_summary_verifier_agent = TaskFromSummaryVerifierAgent(self.prompt_loader)
        self.task_from_backlog_verifier_agent = TaskFromBacklogVerifierAgent(self.prompt_loader)


    def create_save_summary_tasks_use_case(self, member_repo: IMemberRepository) -> SaveSummaryTasksInClickUpUseCase:
        """
        Factory method for SaveSummaryTasksInClickUpUseCase.

        Combines ClickUp infrastructure with a request-scoped member repository
        to persist generated summary tasks into ClickUp.

        Args:
            member_repo: Request-scoped member repository.

        Returns:
            SaveSummaryTasksInClickUpUseCase: Fully initialized use case.

        Raises:
            ServiceUnavailableException: If ClickUp infrastructure is not available.
        """
        if self.clickup_reader is None:
            raise ServiceUnavailableException("ClickUp task service is currently unavailable. Please try again later.")

        if self.clickup_writer is None:
            raise ServiceUnavailableException("ClickUp service service is currently unavailable. Please try again later.")

        return SaveSummaryTasksInClickUpUseCase(
            clickup_reader=self.clickup_reader,
            member_repo=member_repo,
            clickup_writer=self.clickup_writer,
        )

    def create_save_backlog_tasks_use_case(self, member_repo: IMemberRepository) -> SaveBacklogTasksInClickUpUseCase:
        """
        Factory method for SaveBacklogTasksInClickUpUseCase.

        Combines singleton ClickUp infrastructure with a request-scoped member_repo.

        Args:
            member_repo: Request-scoped member repository.

        Returns:
            SaveBacklogTasksInClickUpUseCase: Fully initialized use case.

        Raises:
            ServiceUnavailableException: If ClickUp infrastructure is not initialized.
        """
        if self.clickup_reader is None:
            raise ServiceUnavailableException("ClickUp task service is currently unavailable. Please try again later.")

        if self.clickup_writer is None:
            raise ServiceUnavailableException("ClickUp service is currently unavailable. Please try again later.")

        return SaveBacklogTasksInClickUpUseCase(
            clickup_reader=self.clickup_reader,
            member_repo=member_repo,
            clickup_writer=self.clickup_writer,
        )

    def create_tasks_from_summary_verification_use_case(self, member_repo: IMemberRepository) -> VerifyTasksFromSummaryUseCase:
        """
        Factory method for VerifyTasksFromSummaryUseCase.

        This method creates a use case responsible for verifying generated ClickUp.

        It combines:
            - The external member service (repository abstraction)
            - The ClickUp workspace reader infrastructure component
            - the agent who verify the tasks

        Args:
            member_repo (IMemberRepository): Request-scoped member repository.

        Returns:
            VerifyTasksFromSummaryUseCase: Fully initialized use case ready to verify generated ClickUp.

        Raises:
            ServiceUnavailableException: If required ClickUp writer infrastructure is not initialized.
        """
        if self.clickup_reader is None:
            raise ServiceUnavailableException("ClickUp service is currently unavailable. Please try again later.")

        if self.task_from_summary_verifier_agent is None:
            raise ServiceUnavailableException(
                "Task verification service is currently unavailable. Please try again later.")

        return VerifyTasksFromSummaryUseCase(
            clickup_reader=self.clickup_reader,
            task_verifier=self.task_from_summary_verifier_agent,
            member_repo=member_repo,
        )

    def create_tasks_from_backlog_verification_use_case(self, member_repo: IMemberRepository) -> VerifyTasksFromBacklogUseCase:
        """
        Factory method for VerifyTasksFromBacklogUseCase.

        This method creates a use case responsible for verifying generated ClickUp.

        It combines:
            - The external member service (repository abstraction)
            - The ClickUp workspace reader infrastructure component
            - the agent who verify the tasks

        Args:
            member_repo (IMemberRepository): Request-scoped member repository.

        Returns:
            VerifyTasksFromBacklogUseCase: Fully initialized use case ready to verify generated ClickUp.

        Raises:
            ServiceUnavailableException: If required ClickUp writer infrastructure is not initialized.
        """
        if self.clickup_reader is None:
            raise ServiceUnavailableException("ClickUp service is currently unavailable. Please try again later.")

        if self.task_from_backlog_verifier_agent is None:
            raise ServiceUnavailableException(
                "Task verification service is currently unavailable. Please try again later.")

        return VerifyTasksFromBacklogUseCase(
            clickup_reader=self.clickup_reader,
            task_verifier=self.task_from_backlog_verifier_agent,
            member_repo=member_repo,
        )