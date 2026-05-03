"""
Dependency container for backlog generation workflow.

This module defines the BacklogContainer class, which wires together agents, tools,
and orchestrators required for backlog generation using LLM-based workflows.

Classes:
    BacklogContainer: Dependency injection container for backlog agents, tools, and orchestrators.
"""

import logging

from backend.src.application.use_cases.generate_backlog_use_case import GenerateBacklogUseCase

from backend.src.domain.exceptions.base.app_exception import AppException

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
from backend.src.infrastructure.prompts.prompt_loader import PromptLoader


logger = logging.getLogger(__name__)


class BacklogContainer:
    """
    Dependency injection container for backlog generation workflow.

    This container is responsible for initializing and wiring all components required
    for backlog generation, including agents, tools, and workflow orchestrators.

    Attributes:
        prompt_loader (PromptLoader): Loader for prompt templates.
        backlog_workflow_orchestrator (BacklogWorkflowOrchestrator | None): Workflow orchestrator instance.
        generate_backlog_use_case (GenerateBacklogUseCase | None): Use case for backlog generation.

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
        Initialize backlog container dependencies.

        Raises:
            AppException: If container initialization fails.
        """
        logger.info("Initializing backlog container.")

        self.backlog_workflow_orchestrator: BacklogWorkflowOrchestrator | None = None
        self.generate_backlog_use_case: GenerateBacklogUseCase | None = None

        try:
            self._init_backlog_agents()
            self._init_backlog_tools()

            logger.info("Backlog container initialized successfully.")

        except Exception as e:
            logger.exception("Failed to initialize backlog container.")
            raise AppException("Failed to initialize container.", "CONTAINER_INIT_ERROR") from e

    # Agents
    def _init_backlog_agents(self):
        """
        Initialize backlog generation agents.

        This method creates all LLM-based agents responsible for generating
        epics, user stories, tasks, and other backlog-related elements.
        """
        logger.info("Initializing backlog generation agents.")

        self.prompt_loader = PromptLoader()

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
        Initialize backlog generation tools.

        This method creates tool wrappers around agents to expose them as
        callable units for orchestration workflows.
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

        This method must be called once at application startup before handling
        backlog-related requests.
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

        This method must be called once at application startup before using
        any web search functionality.
        """
        await self.web_search_agent.create()

    async def backlog_workflow_orchestrator_factory(self) -> BacklogWorkflowOrchestrator:
        """
        Create a backlog workflow orchestrator instance.

        This method is useful for scripts or standalone executions where the
        full container initialization is not required.

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

    # backlog_container.py — ajouter cette méthode

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