"""
Backlog generation orchestrator agent.

This module defines the BacklogGenerationOrchestratorAgent, which coordinates multiple
specialized LLM agents to generate a full backlog structure (epics, user stories, tasks)
from a product description and market intelligence context.
"""

import logging

import asyncio
from concurrent.futures import ThreadPoolExecutor

from backend.src.domain.entities.backlog.backlog_structure import BacklogStructure, EpicBacklog, UserStoryWithTasks
from backend.src.domain.entities.backlog.epic import Epic
from backend.src.domain.entities.market.refined_market_intelligence import RefinedMarketIntelligenceSummary
from backend.src.domain.entities.product.initial_description import InitialDescription
from backend.src.domain.exceptions.backlog.backlog_generation_exception import BacklogGenerationException
from backend.src.domain.ports.services.backlog_generation.agents.ibacklog_cleaner import IBacklogCleaner
from backend.src.domain.ports.services.backlog_generation.agents.ibacklog_generation_orchestrator import \
    IBacklogGenerationOrchestrator
from backend.src.domain.ports.services.backlog_generation.agents.iepic_generator import IEpicGenerator
from backend.src.domain.ports.services.backlog_generation.agents.itask_generator import ITaskGenerator
from backend.src.domain.ports.services.backlog_generation.agents.iuser_strory_generator import IUserStoryGenerator


logger = logging.getLogger(__name__)


class BacklogGenerationOrchestratorAgent(IBacklogGenerationOrchestrator):
    """
    Orchestrates the full backlog generation pipeline.

    This class is responsible for coordinating multiple AI agents to transform
    a product description into a structured backlog.

    Responsibilities:
        - Generate epics
        - Generate user stories per epic
        - Generate tasks per user story
        - Clean and validate final backlog structure

    Attributes:
        epic_generator (IEpicGenerator): Agent responsible for epic generation.
        user_story_generator (IUserStoryGenerator): Agent responsible for user story generation.
        task_generator (ITaskGenerator): Agent responsible for task generation.
        backlog_cleaner (IBacklogCleaner): Agent responsible for backlog validation and cleaning.
    """

    def __init__(
        self,
        epic_generator: IEpicGenerator,
        user_story_generator: IUserStoryGenerator,
        task_generator: ITaskGenerator,
        backlog_cleaner: IBacklogCleaner
    ):
        """
        Initialize the backlog generation orchestrator.

        Args:
            epic_generator (IEpicGenerator): Epic generation agent.
            user_story_generator (IUserStoryGenerator): User story generator agent.
            task_generator (ITaskGenerator): Task generator agent.
            backlog_cleaner (IBacklogCleaner): Backlog cleaner agent.
        """
        self.epic_generator = epic_generator
        self.user_story_generator = user_story_generator
        self.task_generator = task_generator
        self.backlog_cleaner = backlog_cleaner

    async def generate(
            self,
            detailed_description: InitialDescription,
            context: RefinedMarketIntelligenceSummary
    ) -> BacklogStructure:
        """
        Generate a full backlog structure.

        Workflow:
            1. Generate epics
            2. Generate user stories + tasks per epic (parallel execution)
            3. Clean final backlog

        Args:
            detailed_description (InitialDescription): Product description.
            context (RefinedMarketIntelligenceSummary): Market intelligence context.

        Returns:
            BacklogStructure: Final cleaned backlog.

        Raises:
            BacklogGenerationException: If generation pipeline fails.
        """
        logger.info("Starting backlog generation workflow.")

        try:
            loop = asyncio.get_running_loop()

            with ThreadPoolExecutor() as executor:
                epics_response = await loop.run_in_executor(
                    executor,
                    self.epic_generator.generate_epics,
                    detailed_description,
                    context
                )
                epics = epics_response.epics

                results = await asyncio.gather(*[
                    loop.run_in_executor(
                        executor,
                        self._process_epic_sync,
                        epic,
                        detailed_description,
                        context
                    )
                    for epic in epics
                ], return_exceptions=True)

            valid = []
            for epic, result in zip(epics, results):
                if isinstance(result, EpicBacklog):
                    valid.append(result)
                else:
                    logger.error(
                        "Epic processing failed (epic=%s): %s.",
                        getattr(epic, "title", epic),
                        result
                    )

            if not valid:
                raise BacklogGenerationException(
                    "All epics failed to process. No valid backlog could be generated."
                )

            logger.info(
                "Epic processing completed. Valid=%d / Total=%d.",
                len(valid),
                len(epics)
            )

            cleaned_backlog = self.backlog_cleaner.clean_backlog(BacklogStructure(epics=valid))

            logger.info("Backlog generation completed successfully.")

            return cleaned_backlog
        except BacklogGenerationException:
            raise
        except Exception as e:
            logger.exception("Backlog generation failed.")
            raise BacklogGenerationException(
                "Failed to generate backlog."
            ) from e

    def _process_epic_sync(
        self,
        epic: Epic,
        detailed_description: InitialDescription,
        context: RefinedMarketIntelligenceSummary
    ) -> EpicBacklog:
        """
        Process a single epic synchronously.

        Steps:
            - Generate user stories
            - Generate tasks for each user story
            - Build EpicBacklog structure

        Args:
            epic (Epic): Epic to process.
            detailed_description (InitialDescription): Product description.
            context (RefinedMarketIntelligenceSummary): Market context.

        Returns:
            EpicBacklog: Processed epic with user stories and tasks.
        """
        user_stories_response = self.user_story_generator.generate_user_stories_by_epic(
            epic, detailed_description, context
        )
        tasks_results = [
            self.task_generator.generate_tasks_by_user_story(us, detailed_description, context)
            for us in user_stories_response.user_stories
        ]
        return EpicBacklog(
            epic=epic,
            user_stories=[
                UserStoryWithTasks(user_story=us, tasks=tr.tasks)
                for us, tr in zip(user_stories_response.user_stories, tasks_results)
            ]
        )