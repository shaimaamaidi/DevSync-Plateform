"""
Sprint planner orchestrator.

This module defines the SprintPlannerOrchestrator, responsible for generating
end-to-end sprint planning from a structured backlog using a hybrid LLM pipeline.

The orchestrator coordinates multiple agents to transform a prioritized backlog into
time-boxed sprint plans:

Pipeline overview:
- Extract and build global backlog context
- Estimate tasks per epic using TaskEstimatorAgent (LLM-based decomposition)
- Build sprint-ready user story representations
- Group stories into sprints using SprintGrouperAgent (LLM-based clustering)
- Produce final SprintPlanning output

This class acts as a high-level orchestration layer combining:
- LLM-based task estimation
- LLM-based sprint grouping
- Deterministic aggregation logic (hours, mappings, validation)
"""

import asyncio
import logging
import uuid
from typing import List

from backend.src.domain.entities.backlog.structure import BacklogStructure, EpicBacklog
from backend.src.domain.entities.backlog.user_story import UserStory
from backend.src.domain.entities.sprint.estimation import EstimatedTask
from backend.src.domain.entities.sprint.planning import SprintPlanning
from backend.src.domain.entities.sprint.sprint import UserStorySprint
from backend.src.domain.ports.services.backlog_generation.agents.i_sprint_grouper import ISprintGrouper
from backend.src.domain.ports.services.backlog_generation.agents.i_sprint_planner import ISprintPlanner
from backend.src.domain.ports.services.backlog_generation.agents.i_task_estimator import ITaskEstimator


logger = logging.getLogger(__name__)


class SprintPlannerOrchestrator(ISprintPlanner):
    """
    Orchestrates end-to-end sprint planning from a structured backlog.

    This orchestrator coordinates multiple LLM-based agents to transform a
    backlog into sprint-ready planning structures.

    Responsibilities:
    - Build global context from backlog
    - Trigger task estimation per epic (TaskEstimatorAgent)
    - Generate sprint-ready user stories with unique IDs
    - Group stories into sprints (SprintGrouperAgent)
    - Compute and assemble final SprintPlanning output

    The design follows a hybrid approach:
    - LLM handles semantic reasoning (estimation + grouping)
    - Python handles deterministic aggregation and mapping
    """

    def __init__(
        self,
        task_estimator: ITaskEstimator,
        sprint_grouper: ISprintGrouper
    ):
        """
        Initialize the SprintGeneratorAgent.

        This agent is responsible for generating sprint structures by:
        - Estimating effort for tasks using a task estimation service
        - Grouping estimated tasks into coherent sprints using a sprint grouping strategy

        Args:
            task_estimator (ITaskEstimator):
                Service responsible for estimating effort (in hours) for each task.

            sprint_grouper (ISprintGrouper):
                Service responsible for grouping estimated tasks into structured sprints
                based on workload balancing and logical coherence.
        """
        self._task_estimator = task_estimator
        self._sprint_grouper = sprint_grouper

    def plan_sprints(self, backlog: BacklogStructure) -> SprintPlanning:
        """
        Generate sprint planning from a structured backlog.

        This is the main entry point of the orchestrator. It coordinates the full
        pipeline from backlog → estimation → sprint grouping → sprint planning.

        Steps:
        1. Build textual context from backlog structure
        2. Estimate all epics asynchronously using TaskEstimatorAgent
        3. Build story lookup (story_id → UserStorySprint)
        4. Generate sprint grouping using SprintGrouperAgent
        5. Return final SprintPlanning object

        Args:
            backlog (BacklogStructure): Prioritized backlog containing epics
                and user stories to be planned into sprints.

        Returns:
            SprintPlanning: Final structured sprint plan with grouped sprints
                and estimated workloads.

        Raises:
            LLMNetworkException: If communication with LLM fails.
            LLMApiException: If LLM returns an error response.
            LLMParsingException: If LLM output cannot be parsed correctly.
        """
        logger.info("Starting sprint planning process.")


        context = SprintPlannerOrchestrator._build_context(backlog)

        story_lookup, epic_summaries = asyncio.run(
            self._estimate_all_epics(context, backlog.epics)
        )

        result: SprintPlanning = self._sprint_grouper.group_sprints(epic_summaries, story_lookup)

        logger.info("Sprint planning completed successfully.")
        return result

    async def _estimate_all_epics(
            self,
            context: str,
            epics: List[EpicBacklog],
    ) -> tuple[dict[str, UserStorySprint], str]:
        """
        Estimate all epics in parallel using the TaskEstimatorAgent.

        This method runs asynchronous task estimation for each epic using threads,
        then aggregates:
        - A global story lookup (story_id → UserStorySprint)
        - A textual summary of all epics enriched with estimations

        Processing steps:
        1. Launch parallel estimation tasks per epic
        2. Collect results (story summaries + sprint-ready stories)
        3. Merge all story mappings into a global lookup
        4. Build combined epic summary string

        Args:
            context (str): Global planning context shared across epics.
            epics (List[EpicBacklog]): List of epics to process.

        Returns:
            tuple[dict[str, UserStorySprint], str]:
                - story_lookup: Mapping of generated story IDs to sprint-ready stories
                - epic_summaries: Combined textual representation of all epics
        """
        tasks = [
            asyncio.to_thread(self._estimate_tasks_per_epic, context, epic)
            for epic in epics
        ]

        results = await asyncio.gather(*tasks)

        story_lookup: dict[str, UserStorySprint] = {}
        epic_summaries = []

        for epic_summary, stories in results:
            epic_summaries.append(epic_summary)
            story_lookup.update(stories)

        return story_lookup, "\n".join(epic_summaries)

    def _estimate_tasks_per_epic(
            self,
            context: str,
            epic: EpicBacklog,
    ) -> tuple[str, dict[str, UserStorySprint]]:
        """
        Estimate tasks for a single epic using TaskEstimatorAgent.

        This method:
        - Calls the TaskEstimatorAgent (LLM-based) to decompose user stories
        - Assigns a generated UUID to each story
        - Converts estimated tasks into UserStorySprint objects
        - Builds a human-readable epic summary

        Args:
            context (str): Global planning context.
            epic (EpicBacklog): Epic containing user stories to estimate.

        Returns:
            tuple[str, dict[str, UserStorySprint]]:
                - epic_summary: Textual representation of estimated epic
                - local_stories: Mapping of generated story IDs to sprint-ready stories

        Notes:
            - Each story is assigned a UUID for sprint grouping consistency
            - Total hours are computed as sum of task estimates
        """
        stories_summary_lines = [f"EPIC: {epic.epic.title}"]
        local_stories: dict[str, UserStorySprint] = {}

        results = self._task_estimator.estimate_tasks(context, epic)

        for result in results:
            story_id = str(uuid.uuid4())
            total_hours = sum(t.estimated_hours for t in result.tasks)
            stories_summary_lines.append(
                f"- ID: {story_id}\n"
                f"  Title: {result.user_story.title}\n"
                f"  Hours: {total_hours}\n"
                f"  Description: {result.user_story.description}\n"
            )

            local_stories[story_id] = UserStorySprint(
                user_story=UserStory(
                    title=result.user_story.title,
                    description=result.user_story.description
                ),
                tasks=[
                    EstimatedTask(
                        title=t.title,
                        description=t.description,
                        estimated_hours=t.estimated_hours
                    )
                    for t in result.tasks
                ]
            )

        return "\n".join(stories_summary_lines), local_stories

    @staticmethod
    def _build_context(backlog: BacklogStructure) -> str:
        """
        Build a textual context representation from the backlog.

        This method transforms the structured backlog into a readable string
        format that is used as global context for LLM prompts.

        Args:
            backlog (BacklogStructure): Structured backlog containing epics.

        Returns:
            str: Human-readable backlog context including epics titles and descriptions.

        Notes:
            - Only epic-level information is included
            - Used to improve LLM reasoning consistency across estimations
        """
        context = []

        for epic_block in backlog.epics:
            epic = epic_block.epic
            context.append(f"EPIC: {epic.title} — {epic.description}")
            context.append("")

        return "\n".join(context)