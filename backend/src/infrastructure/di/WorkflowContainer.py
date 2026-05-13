"""
Dependency container for backlog generation workflow.

This module defines the WorkflowContainer class, which wires together agents,
tools, external adapters, and use cases required for backlog generation using
LLM-based workflows.

The container is responsible for initializing all components required for:
- Backlog generation (epics, user stories, tasks)
- Market intelligence processing
- ClickUp integration
- Task verification and persistence
- Workflow orchestration

Classes:
    WorkflowContainer: Request/application-scoped dependency injection container.
"""

import logging

from backend.src.application.use_cases.clickup_space_task_reader_use_case import ClickUpSpaceTaskReaderUseCase
from backend.src.application.use_cases.clickup_structure_creation_use_case import ClickUpStructureCreationUseCase
from backend.src.application.use_cases.clickup_structure_metadata_use_case import ClickUpStructureMetadataUseCase
from backend.src.application.use_cases.clickup_task_management_use_case import ClickUpTaskManagementUseCase
from backend.src.application.use_cases.generate_backlog_use_case import GenerateBacklogUseCase
from backend.src.application.use_cases.generate_task_from_summary_use_case import GenerateTaskFromSummaryUseCase
from backend.src.application.use_cases.save_task_in_clickup_use_case import SaveTaskInClickUpUseCase
from backend.src.application.use_cases.verify_task_use_case import VerifyTaskUseCase

from backend.src.domain.exceptions.base.app_exception import AppException
from backend.src.domain.exceptions.system.service_unavailable_exception import ServiceUnavailableException
from backend.src.domain.ports.repositories.i_clickup_repository import IClickUpRepository
from backend.src.domain.ports.repositories.i_member_repository import IMemberRepository

from backend.src.infrastructure.external.backlog_generation.agents.epic_generator_agent import EpicGeneratorAgent
from backend.src.infrastructure.external.backlog_generation.agents.user_story_generator_agent import UserStoryGeneratorAgent
from backend.src.infrastructure.external.backlog_generation.agents.task_generator_agent import TaskGeneratorAgent
from backend.src.infrastructure.external.backlog_generation.agents.backlog_cleaner_agent import BacklogCleanerAgent
from backend.src.infrastructure.external.backlog_generation.agents.backlog_generation_orchestrator_agent import BacklogGenerationOrchestratorAgent
from backend.src.infrastructure.external.backlog_generation.agents.backlog_prioritizer_agent import BacklogPrioritizerAgent
from backend.src.infrastructure.external.backlog_generation.agents.sprint_planner_agent import SprintPlannerAgent
from backend.src.infrastructure.external.backlog_generation.agents.product_context_builder_agent import ProductContextBuilderAgent
from backend.src.infrastructure.external.backlog_generation.agents.market_intelligence_summarizer_agent import MarketIntelligenceSummarizerAgent
from backend.src.infrastructure.external.backlog_generation.agents.market_intelligence_validator_agent import MarketIntelligenceValidatorAgent
from backend.src.infrastructure.external.backlog_generation.agents.market_query_generator_agent import MarketQueryGeneratorAgent
from backend.src.infrastructure.external.backlog_generation.agents.user_backlog_fixer_agent import UserBacklogFixerAgent
from backend.src.infrastructure.external.backlog_generation.agents.web_search_agent import WebSearchAgent

from backend.src.infrastructure.external.backlog_generation.tools.product_context_builder_tool import ProductContextBuilderTool
from backend.src.infrastructure.external.backlog_generation.tools.market_query_generator_tool import MarketQueryGeneratorTool
from backend.src.infrastructure.external.backlog_generation.tools.web_search_tool import WebSearchTool
from backend.src.infrastructure.external.backlog_generation.tools.market_summarizer_tool import MarketSummarizerTool
from backend.src.infrastructure.external.backlog_generation.tools.market_validator_tool import MarketValidatorTool
from backend.src.infrastructure.external.backlog_generation.tools.backlog_generator_tool import BacklogGeneratorTool
from backend.src.infrastructure.external.backlog_generation.tools.user_backlog_fixer_tool import UserBacklogFixerTool
from backend.src.infrastructure.external.backlog_generation.tools.delivery_planner_tool import DeliveryPlannerTool

from backend.src.infrastructure.external.backlog_generation.orchestrator.backlog_workflow_orchestrator import BacklogWorkflowOrchestrator
from backend.src.infrastructure.external.clickup.clickup_reader import ClickUpReader
from backend.src.infrastructure.external.clickup.writer.clickup_task_writer import ClickUpTaskWriter
from backend.src.infrastructure.external.clickup.client.clickup_http_client import ClickUpHttpClient
from backend.src.infrastructure.external.clickup.writer.clickup_workspace_writer import ClickUpWorkSpaceWriter
from backend.src.infrastructure.external.clickup_task_verification.clickup_task_verifier_agent import \
    ClickUpTaskVerifierAgent
from backend.src.infrastructure.external.task_generation_from_summary.clickup_task_generator_agent import \
    ClickUpTaskGeneratorAgent
from backend.src.infrastructure.prompts.prompt_loader import PromptLoader


logger = logging.getLogger(__name__)


class WorkflowContainer:
    """
    Dependency injection container for backlog generation workflow.

    This container wires together all components required for backlog generation,
    including LLM agents, tools, ClickUp infrastructure, and orchestration layers.

    Responsibilities:
        - Initialize LLM-based backlog generation agents
        - Initialize tool wrappers for workflow execution
        - Manage ClickUp external service integration
        - Provide use cases for backlog generation and task processing
        - Expose factory methods for request-scoped operations

    Attributes:
        # Core orchestration
        backlog_workflow_orchestrator (BacklogWorkflowOrchestrator | None):
            Main orchestrator for the backlog generation workflow.
        generate_backlog_use_case (GenerateBacklogUseCase | None):
            Use case responsible for executing backlog generation.

        # ClickUp infrastructure
        clickup_writer (ClickUpTaskWriter | None): Service for writing tasks to ClickUp.
        clickup_workspace_writer (ClickUpWorkSpaceWriter | None): Service for writing ClickUp workspace structure.
        http_client (ClickUpHttpClient): HTTP client used for ClickUp API communication.
        clickup_reader (ClickUpReader): Reader adapter for ClickUp data access.

        # Task-related use cases
        clickup_task_generator_use_case (GenerateTaskFromSummaryUseCase | None):
            Use case for generating ClickUp tasks from a summary.
        clickup_structure_metadata_use_case (ClickUpStructureMetadataUseCase | None):
            Use case responsible for retrieving ClickUp workspace structure metadata.
        clickup_space_task_reader_use_case (ClickUpSpaceTaskReaderUseCase | None):
            Use case responsible for retrieving ClickUp tasks by un space id
        clickup_task_creation_use_case (ClickUpTaskManagementUseCase | None):
            Use case responsible for creating, updating and deleting ClickUp tasks

        # Prompt system
        prompt_loader (PromptLoader): Loader responsible for retrieving LLM prompt templates.

        # Agents
        epic_generator_agent (EpicGeneratorAgent)
        user_story_generator_agent (UserStoryGeneratorAgent)
        task_generator_agent (TaskGeneratorAgent)
        backlog_cleaner_agent (BacklogCleanerAgent)
        backlog_prioritizer_agent (BacklogPrioritizerAgent)
        sprint_planner_agent (SprintPlannerAgent)

        product_context_builder_agent (ProductContextBuilderAgent)
        market_intelligence_summarizer_agent (MarketIntelligenceSummarizerAgent)
        market_intelligence_validator_agent (MarketIntelligenceValidatorAgent)
        market_query_generator_agent (MarketQueryGeneratorAgent)

        user_backlog_fixer_agent (UserBacklogFixerAgent)
        web_search_agent (WebSearchAgent)

        backlog_generation_orchestrator_agent (BacklogGenerationOrchestratorAgent):
            Orchestrates epic → story → task generation pipeline.

        # Tools
        product_context_tool (ProductContextBuilderTool)
        market_query_tool (MarketQueryGeneratorTool)
        web_search_tool (WebSearchTool)
        market_summary_tool (MarketSummarizerTool)
        market_validation_tool (MarketValidatorTool)

        backlog_generation_tool (BacklogGeneratorTool)
        user_backlog_fixer_tool (UserBacklogFixerTool)

        delivery_planning_tool (DeliveryPlannerTool): Tool responsible for sprint planning and prioritization.
    """

    def __init__(self):
        """
        Initialize workflow container dependencies.

        Raises:
            AppException: If container initialization fails.
        """
        logger.info("Initializing workflow container.")

        self.backlog_workflow_orchestrator: BacklogWorkflowOrchestrator | None = None
        self.generate_backlog_use_case: GenerateBacklogUseCase | None = None

        self.clickup_writer: ClickUpTaskWriter | None = None
        self.clickup_workspace_writer: ClickUpWorkSpaceWriter | None = None


        self.clickup_task_generator_use_case: GenerateTaskFromSummaryUseCase | None = None
        self.clickup_structure_metadata_use_case: ClickUpStructureMetadataUseCase | None = None
        self.clickup_space_task_reader_use_case: ClickUpSpaceTaskReaderUseCase | None = None
        self.clickup_task_creation_use_case: ClickUpTaskManagementUseCase | None = None

        self.prompt_loader = PromptLoader()

        try:
            self._init_backlog_agents()
            self._init_backlog_tools()

            self._init_clickup_external_service()
            self._init_tasks_generation_from_summary()
            self._init_tasks_verification_agent()
            self._init_clickup_structure_metadata_use_case()
            self._init_clickup_space_task_reader_use_case()
            self._init_clickup_task_creation_use_case()

            logger.info("Workflow container initialized successfully.")

        except Exception as e:
            logger.exception("Failed to initialize workflow container.")
            raise AppException("Failed to initialize workflow container.", "CONTAINER_INIT_ERROR") from e

    # Agents
    def _init_backlog_agents(self):
        """
        Initialize LLM-based backlog generation agents.

        These agents are responsible for generating and refining:
        - Epics
        - User stories
        - Tasks
        - Market intelligence insights
        - Backlog cleanup and prioritization
        """
        logger.info("Initializing backlog generation agents.")

        self.epic_generator_agent = EpicGeneratorAgent(self.prompt_loader)
        self.user_story_generator_agent = UserStoryGeneratorAgent(self.prompt_loader)
        self.task_generator_agent = TaskGeneratorAgent(self.prompt_loader)
        self.backlog_cleaner_agent = BacklogCleanerAgent(self.prompt_loader)
        self.backlog_prioritizer_agent = BacklogPrioritizerAgent(self.prompt_loader)
        self.sprint_planner_agent = SprintPlannerAgent(self.prompt_loader)
        self.product_context_builder_agent = ProductContextBuilderAgent(self.prompt_loader)
        self.market_intelligence_summarizer_agent = MarketIntelligenceSummarizerAgent(self.prompt_loader)
        self.market_intelligence_validator_agent = MarketIntelligenceValidatorAgent(self.prompt_loader)
        self.market_query_generator_agent = MarketQueryGeneratorAgent(self.prompt_loader)
        self.user_backlog_fixer_agent = UserBacklogFixerAgent(self.prompt_loader)
        self.web_search_agent = WebSearchAgent()

        self.backlog_generation_orchestrator_agent = BacklogGenerationOrchestratorAgent(
            epic_generator=self.epic_generator_agent,
            user_story_generator=self.user_story_generator_agent,
            task_generator=self.task_generator_agent,
            backlog_cleaner=self.backlog_cleaner_agent,
        )

    # Backlog generation — Tools
    def _init_backlog_tools(self):
        """
        Initialize workflow tools wrapping agents into executable units.
        """
        logger.info("Initializing backlog generation tools.")

        self.product_context_tool  = ProductContextBuilderTool(self.product_context_builder_agent)
        self.market_query_tool     = MarketQueryGeneratorTool(self.market_query_generator_agent)
        self.web_search_tool       = WebSearchTool(self.web_search_agent)
        self.market_summary_tool   = MarketSummarizerTool(self.market_intelligence_summarizer_agent)
        self.market_validation_tool = MarketValidatorTool(self.market_intelligence_validator_agent)
        self.backlog_generation_tool = BacklogGeneratorTool(self.backlog_generation_orchestrator_agent)
        self.user_backlog_fixer_tool = UserBacklogFixerTool(self.user_backlog_fixer_agent)
        self.delivery_planning_tool  = DeliveryPlannerTool(
            backlog_prioritizer = self.backlog_prioritizer_agent,
            sprint_planner      = self.sprint_planner_agent,
        )

    async def initialize_backlog_workflow_orchestrator(self):
        """
        Initialize the backlog workflow orchestrator and use case.
        """
        logger.info("Initializing BacklogWorkflowOrchestrator.")

        self.backlog_workflow_orchestrator = await BacklogWorkflowOrchestrator.create(
            product_context_tool=self.product_context_tool,
            query_generator_tool=self.market_query_tool,
            web_search_tool=self.web_search_tool,
            market_summarizer_tool=self.market_summary_tool,
            market_validator_tool=self.market_validation_tool,
            backlog_generator_tool=self.backlog_generation_tool,
            user_backlog_fixer_tool=self.user_backlog_fixer_tool,
            delivery_planner_tool=self.delivery_planning_tool,
        )

        self.generate_backlog_use_case = GenerateBacklogUseCase(
            orchestrator=self.backlog_workflow_orchestrator
        )

    async def initialize_web_search_tool(self):
        """
        Initialize the web search agent.
        """
        await self.web_search_agent.create()

    async def backlog_workflow_orchestrator_factory(self) -> BacklogWorkflowOrchestrator:
        """
        Create a backlog workflow orchestrator instance.

        Returns:
            BacklogWorkflowOrchestrator: Initialized orchestrator instance.
        """
        return await BacklogWorkflowOrchestrator.create(
            product_context_tool=self.product_context_tool,
            query_generator_tool=self.market_query_tool,
            web_search_tool=self.web_search_tool,
            market_summarizer_tool=self.market_summary_tool,
            market_validator_tool=self.market_validation_tool,
            backlog_generator_tool=self.backlog_generation_tool,
            user_backlog_fixer_tool=self.user_backlog_fixer_tool,
            delivery_planner_tool=self.delivery_planning_tool,
        )

    async def cleanup(self) -> None:
        """
        Release all persistent network resources held by the container.

        Closes the web search agent session and the workflow orchestrator.
        Pure LLM agents are stateless and require no explicit cleanup.
        """
        logger.info("Cleaning up backlog container resources.")

        if self.web_search_agent is not None:
            try:
                await self.web_search_agent.cleanup()
                logger.info("Web search agent closed.")
            except Exception:
                logger.warning("Failed to close web search agent.", exc_info=True)

        if self.backlog_workflow_orchestrator is not None:
            try:
                await self.backlog_workflow_orchestrator.cleanup()
                logger.info("Backlog workflow orchestrator closed.")
            except Exception:
                logger.warning("Failed to close backlog workflow orchestrator.", exc_info=True)

        logger.info("Backlog container cleanup complete.")

    def _init_clickup_external_service(self):
        """
        Initialize ClickUp HTTP client, reader, writers, and task service.
        """
        logger.info("Initializing ClickUp external service.")

        self.http_client = ClickUpHttpClient()
        self.clickup_reader = ClickUpReader(self.http_client)
        self.clickup_writer = ClickUpTaskWriter(self.http_client)
        self.clickup_workspace_writer = ClickUpWorkSpaceWriter(self.http_client)

    def _init_tasks_generation_from_summary(self):
        """
        Initialize the task generation from summary use case.
        """
        logger.info("Initializing task generation from summary use case.")

        self.clickup_task_generator_agent = ClickUpTaskGeneratorAgent(self.prompt_loader)
        self.clickup_task_generator_use_case = GenerateTaskFromSummaryUseCase(
            self.clickup_reader,
            self.clickup_task_generator_agent,
        )

    def _init_tasks_verification_agent(self):
        """
        Initialize the task verification use case.
        """
        logger.info("Initializing task verification agent.")

        self.clickup_task_verifier_agent = ClickUpTaskVerifierAgent(self.prompt_loader)

    def _init_clickup_structure_metadata_use_case(self):
        """
        Initialize ClickUpStructureMetadataUseCase.

        This method wires the ClickUp structure metadata use case responsible for
        retrieving workspace structure information such as:
            - Spaces
            - Folders
            - Lists
            - Status configurations

        The use case relies on the ClickUpReader infrastructure to fetch data
        from the ClickUp API.

        Raises:
            AppException:
                If required ClickUp infrastructure is not properly initialized.
        """
        logger.info("Initializing ClickUpStructureMetadataUseCase.")

        self.clickup_structure_metadata_use_case = ClickUpStructureMetadataUseCase(
            self.clickup_reader
        )

    def _init_clickup_task_creation_use_case(self):
        """
        Initialize ClickUpTaskManagementUseCase.

        This method wires the use case responsible for managing ClickUp tasks,
        including creation, update, and deletion operations.

        It injects the required ClickUp infrastructure components:
            - ClickUpTaskWriter for write operations (create, update, delete)
            - ClickUpReader for retrieving workspace and member data

        The resulting use case acts as the application layer entry point
        for task lifecycle management.
        """
        logger.info("Initializing ClickUpTaskManagementUseCase.")

        self.clickup_task_creation_use_case = ClickUpTaskManagementUseCase(
            self.clickup_writer,
            self.clickup_reader,
        )

    def _init_clickup_space_task_reader_use_case(self):
        """
        Initialize ClickUpSpaceTaskReaderUseCase.

        This method wires the use case responsible for retrieving tasks
        associated with a specific ClickUp space.

        It uses the ClickUpReader infrastructure to fetch task data from
        the ClickUp API without applying any business transformation or caching.

        The resulting use case provides read-only access to space-level tasks
        within the ClickUp workspace.
        """
        logger.info("Initializing ClickUpSpaceTaskReaderUseCase.")

        self.clickup_space_task_reader_use_case = ClickUpSpaceTaskReaderUseCase(
            self.clickup_reader
        )

    def create_save_task_use_case(self, member_repo: IMemberRepository) -> SaveTaskInClickUpUseCase:
        """
        Factory method for SaveTaskInClickUpUseCase.

        Combines singleton ClickUp infrastructure with a request-scoped member_repo.

        Args:
            member_repo: Request-scoped member repository.

        Returns:
            SaveTaskInClickUpUseCase: Fully initialized use case.

        Raises:
            ServiceUnavailableException: If ClickUp infrastructure is not initialized.
        """
        if self.clickup_reader is None:
            raise ServiceUnavailableException("ClickUp task service is not initialized.")

        if self.clickup_writer is None:
            raise ServiceUnavailableException("ClickUp writer is not initialized.")

        return SaveTaskInClickUpUseCase(
            clickup_reader=self.clickup_reader,
            member_repo=member_repo,
            clickup_writer=self.clickup_writer,
        )

    def create_clickup_structure_creation_use_case(self, clickup_repo: IClickUpRepository) -> ClickUpStructureCreationUseCase:
        """
        Factory method for ClickUpStructureCreationUseCase.

        This method creates a use case responsible for building ClickUp workspace
        structure, including spaces, folders, lists, and statuses.

        It combines:
            - The external ClickUp service (repository abstraction)
            - The ClickUp workspace writer infrastructure component

        Args:
            clickup_repo (IClickUpRepository): Request-scoped click up repository.

        Returns:
            ClickUpStructureCreationUseCase:
                Fully initialized use case ready to create ClickUp workspace structure.

        Raises:
            ServiceUnavailableException:
                If required ClickUp writer infrastructure is not initialized.
        """
        if self.clickup_writer is None:
            raise ServiceUnavailableException("ClickUp writer is not initialized.")

        return ClickUpStructureCreationUseCase(
            clickup_repo=clickup_repo,
            clickup_reader=self.clickup_reader,
            clickup_writer=self.clickup_workspace_writer
        )

    def create_tasks_verification_use_case(self, member_repo: IMemberRepository) -> VerifyTaskUseCase:
        """
        Factory method for VerifyTaskUseCase.

        This method creates a use case responsible for verifying generated ClickUp.

        It combines:
            - The external member service (repository abstraction)
            - The ClickUp workspace reader infrastructure component
            - the agent who verify the tasks

        Args:
            member_repo (IMemberRepository): Request-scoped member repository.

        Returns:
            VerifyTaskUseCase:
                Fully initialized use case ready to verify generated ClickUp.

        Raises:
            ServiceUnavailableException:
                If required ClickUp writer infrastructure is not initialized.
        """
        if self.clickup_reader is None:
            raise ServiceUnavailableException("ClickUp writer is not initialized.")

        if self.clickup_task_verifier_agent is None:
            raise ServiceUnavailableException("Verifier agent is not initialized.")

        return VerifyTaskUseCase(
            clickup_reader=self.clickup_reader,
            task_verifier=self.clickup_task_verifier_agent,
            member_repo=member_repo,
        )