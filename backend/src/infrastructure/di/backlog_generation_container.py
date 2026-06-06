"""
Dependency container for backlog generation workflow.

This module defines the BacklogGenerationContainer class, which wires together
LLM-based agents, tools, external adapters, and application use cases required
for backlog generation workflows.

It is responsible for initializing all components required for:
- Backlog generation (epics, user stories, tasks)
- Market intelligence processing and enrichment
- Product context building and web search integration
- Backlog prioritization and sprint planning
- Task generation, cleanup, and orchestration
- ClickUp integration and workflow execution

Classes:
    BacklogGenerationContainer: Request/application-scoped dependency injection container.
"""

import logging

from backend.src.application.use_cases.generate_backlog_use_case import GenerateBacklogUseCase
from backend.src.domain.exceptions.base.app_exception import AppException
from backend.src.infrastructure.di.bas_ai_container import BaseAIContainer

from backend.src.infrastructure.external.backlog_generation.agents.epic_generator_agent import EpicGeneratorAgent
from backend.src.infrastructure.external.backlog_generation.agents.sprint_grouper_agent import SprintGrouperAgent
from backend.src.infrastructure.external.backlog_generation.agents.task_estimator_agent import TaskEstimatorAgent
from backend.src.infrastructure.external.backlog_generation.agents.user_story_generator_agent import UserStoryGeneratorAgent
from backend.src.infrastructure.external.backlog_generation.agents.task_generator_agent import TaskGeneratorAgent
from backend.src.infrastructure.external.backlog_generation.agents.epic_cleaner_agent import EpicCleanerAgent
from backend.src.infrastructure.external.backlog_generation.agents.backlog_generation_orchestrator_agent import BacklogGenerationOrchestratorAgent
from backend.src.infrastructure.external.backlog_generation.agents.backlog_prioritizer_agent import BacklogPrioritizerAgent
from backend.src.infrastructure.external.backlog_generation.agents.sprint_planner_orchestrator import SprintPlannerOrchestrator
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


logger = logging.getLogger(__name__)


class BacklogGenerationContainer(BaseAIContainer):
    """
    Dependency injection container for backlog generation workflow.

    This container orchestrates all dependencies required for backlog generation
    using LLM-powered agents and tool-based workflow execution.

    It is responsible for:
    - Initializing AI prompt-based agents for backlog generation
    - Building tool wrappers around domain agents
    - Managing workflow orchestration for backlog creation
    - Supporting market intelligence enrichment and web search
    - Providing factories for executing backlog generation use cases
    - Cleaning up long-lived workflow resources

    Attributes:
        backlog_workflow_orchestrator (BacklogWorkflowOrchestrator | None):
            Main orchestrator responsible for executing the backlog workflow.
        generate_backlog_use_case (GenerateBacklogUseCase | None):
            Application use case for generating backlog from inputs.

        # Core agents
        epic_generator_agent (EpicGeneratorAgent)
        user_story_generator_agent (UserStoryGeneratorAgent)
        task_generator_agent (TaskGeneratorAgent)
        epic_cleaner_agent (EpicCleanerAgent)
        backlog_prioritizer_agent (BacklogPrioritizerAgent)
        task_estimator_agent (TaskEstimatorAgent)
        sprint_grouper_agent (SprintGrouperAgent)

        product_context_builder_agent (ProductContextBuilderAgent)
        market_intelligence_summarizer_agent (MarketIntelligenceSummarizerAgent)
        market_intelligence_validator_agent (MarketIntelligenceValidatorAgent)
        market_query_generator_agent (MarketQueryGeneratorAgent)
        user_backlog_fixer_agent (UserBacklogFixerAgent)
        web_search_agent (WebSearchAgent)

        sprint_planner_orchestrator_agent (SprintPlannerOrchestrator)
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
        delivery_planning_tool (DeliveryPlannerTool)
    """

    def __init__(self):
        """
        Initialize the BacklogGenerationContainer.

        This constructor sets up:
        - Base AI infrastructure (prompt loading)
        - All backlog-related LLM agents
        - Tool wrappers for agent execution
        - Workflow orchestration components (lazy or async initialization)

        Raises:
            AppException: If any dependency required for backlog generation fails.
        """
        logger.info("Initializing backlog generation container.")

        self.backlog_workflow_orchestrator: BacklogWorkflowOrchestrator | None = None
        self.generate_backlog_use_case: GenerateBacklogUseCase | None = None

        try:
            super().__init__()
            self._init_backlog_agents()
            self._init_backlog_tools()

            logger.info("Backlog generation container initialized successfully.")

        except AppException:
            raise
        except Exception as e:
            logger.exception("Failed to initialize backlog generation container.")
            raise AppException(
                "Backlog generation services are currently unavailable. Please try again later.",
                "BACKLOG_GENERATION_CONTAINER_INIT_ERROR",
                http_status=500,
            ) from e

    # Agents
    def _init_backlog_agents(self):
        """
        Initialize LLM-based backlog generation agents.

        These agents are responsible for:
        - Generating epics, user stories, and tasks
        - Cleaning and refining backlog structure
        - Prioritizing and planning sprint execution
        - Extracting and validating market intelligence
        - Generating queries and performing web search
        - Fixing and improving user-provided backlog inputs
        """
        logger.info("Initializing backlog generation agents.")

        self.epic_generator_agent = EpicGeneratorAgent(self.prompt_loader)
        self.user_story_generator_agent = UserStoryGeneratorAgent(self.prompt_loader)
        self.task_generator_agent = TaskGeneratorAgent(self.prompt_loader)
        self.epic_cleaner_agent = EpicCleanerAgent(self.prompt_loader)
        self.backlog_prioritizer_agent = BacklogPrioritizerAgent(self.prompt_loader)
        self.task_estimator_agent = TaskEstimatorAgent(self.prompt_loader)
        self.sprint_grouper_agent = SprintGrouperAgent(self.prompt_loader)
        self.product_context_builder_agent = ProductContextBuilderAgent(self.prompt_loader)
        self.market_intelligence_summarizer_agent = MarketIntelligenceSummarizerAgent(self.prompt_loader)
        self.market_intelligence_validator_agent = MarketIntelligenceValidatorAgent(self.prompt_loader)
        self.market_query_generator_agent = MarketQueryGeneratorAgent(self.prompt_loader)
        self.user_backlog_fixer_agent = UserBacklogFixerAgent(self.prompt_loader)
        self.web_search_agent = WebSearchAgent()

        self.sprint_planner_orchestrator_agent = SprintPlannerOrchestrator(
            self.task_estimator_agent,
            self.sprint_grouper_agent,
        )
        self.backlog_generation_orchestrator_agent = BacklogGenerationOrchestratorAgent(
            epic_generator=self.epic_generator_agent,
            user_story_generator=self.user_story_generator_agent,
            task_generator=self.task_generator_agent,
            epic_cleaner=self.epic_cleaner_agent,
        )

    # Backlog generation — Tools
    def _init_backlog_tools(self):
        """
        Initialize tool wrappers for backlog generation workflow.

        Tools provide execution layers over LLM agents for:
        - Product context building
        - Market query generation
        - Web search execution
        - Market summarization and validation
        - Backlog generation orchestration
        - User backlog correction
        - Sprint and delivery planning
        """
        logger.info("Initializing backlog generation tools.")

        self.product_context_tool = ProductContextBuilderTool(self.product_context_builder_agent)
        self.market_query_tool = MarketQueryGeneratorTool(self.market_query_generator_agent)
        self.web_search_tool = WebSearchTool(self.web_search_agent)
        self.market_summary_tool = MarketSummarizerTool(self.market_intelligence_summarizer_agent)
        self.market_validation_tool = MarketValidatorTool(self.market_intelligence_validator_agent)
        self.backlog_generation_tool = BacklogGeneratorTool(self.backlog_generation_orchestrator_agent)
        self.user_backlog_fixer_tool = UserBacklogFixerTool(self.user_backlog_fixer_agent)
        self.delivery_planning_tool  = DeliveryPlannerTool(
            backlog_prioritizer=self.backlog_prioritizer_agent,
            sprint_planner=self.sprint_planner_orchestrator_agent,
        )

    async def initialize_backlog_workflow_orchestrator(self):
        """
        Initialize the backlog workflow orchestrator.

        This sets up the runtime orchestration layer responsible for executing
        the full backlog generation pipeline.

        Raises:
            AppException: If orchestrator initialization fails.
        """
        logger.info("Initializing BacklogWorkflowOrchestrator.")
        try:
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
        except Exception as e:
            logger.exception("Failed to initialize BacklogWorkflowOrchestrator.")
            raise AppException(
                "Backlog workflow is currently unavailable. Please try again later.",
                "BACKLOG_ORCHESTRATOR_INIT_ERROR",
                http_status=500,
            ) from e

    async def initialize_web_search_tool(self):
        """
        Initialize the web search agent.

        This prepares the WebSearchAgent for external queries.
        """
        await self.web_search_agent.create()

    async def backlog_workflow_orchestrator_factory(self) -> BacklogWorkflowOrchestrator:
        """
        Factory method for creating a fresh BacklogWorkflowOrchestrator.

        Returns:
            BacklogWorkflowOrchestrator: A new orchestrator instance.
        """
        try:
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
        except Exception as e:
            logger.exception("Failed to create BacklogWorkflowOrchestrator.")
            raise AppException(
                "Backlog workflow is currently unavailable. Please try again later.",
                "BACKLOG_ORCHESTRATOR_FACTORY_ERROR",
                http_status=500,
            ) from e

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
