"""
Sprint grouper agent.

This module defines the SprintGrouperAgent, responsible for grouping
estimated user stories into coherent sprints using an LLM and planning logic.

The agent performs sprint structuring by:
- Grouping user stories into sprint-sized clusters
- Ensuring logical coherence between stories in the same sprint
- Computing total estimated effort per sprint
- Producing a structured sprint planning output

It combines LLM-based grouping with deterministic aggregation logic
to ensure both flexibility and reliability in sprint planning.
"""

import logging

from backend.src.domain.entities.sprint.grouped_sprint import SprintGrouping
from backend.src.domain.entities.sprint.planning import SprintPlanning
from backend.src.domain.entities.sprint.sprint import Sprint, UserStorySprint
from backend.src.domain.ports.services.backlog_generation.agents.i_sprint_grouper import ISprintGrouper
from backend.src.domain.ports.services.prompt_loading.i_prompt_loader import IPromptLoader
from backend.src.infrastructure.external.shared.agents.base_agent import BaseAgent


logger = logging.getLogger(__name__)


class SprintGrouperAgent(BaseAgent[SprintGrouping], ISprintGrouper):
    """
    LLM-based implementation of ISprintGrouper.

    This agent is responsible for:
    - Grouping user stories into sprint-sized clusters using LLM reasoning
    - Building coherent sprint plans from estimated user stories
    - Aggregating task-level estimations into sprint-level metrics
    - Ensuring story lookup consistency across generated sprints

    It combines:
    - LLM-based sprint grouping (SprintGrouping)
    - Deterministic computation of sprint workload
    - Validation of story references via story_lookup
    """

    def __init__(self, prompt_loader: IPromptLoader):
        """
        Initialize the SprintGrouperAgent.

        This constructor injects the prompt loader used for retrieving
        LLM templates responsible for sprint grouping.

        The prompt loader is responsible for:
        - Loading sprint grouping prompts
        - Providing structured LLM templates
        - Ensuring consistent grouping logic across sprint planning

        Args:
            prompt_loader (IPromptLoader): Service responsible for loading
                prompt templates used by the agent during LLM interactions.
        """
        super().__init__(prompt_loader)

    def group_sprints(self, epics: str, story_lookup: dict[str, UserStorySprint]) -> SprintPlanning:
        """
        Generate sprint planning by grouping user stories into coherent sprints.

        This method uses an LLM to group estimated user stories into sprint
        clusters, then resolves each story ID into actual UserStorySprint objects
        using a lookup dictionary. Finally, it computes sprint-level metrics
        such as total estimated hours.

        Processing steps:
        1. Send epics summary to the LLM for sprint grouping
        2. Receive structured SprintGrouping response
        3. Map story IDs to UserStorySprint objects using story_lookup
        4. Compute total estimated hours per sprint
        5. Build final SprintPlanning object

        Args:
            epics (str): Serialized or summarized epics used as input context
                for sprint grouping.
            story_lookup (dict[str, UserStorySprint]): Dictionary mapping
                user story IDs to their estimated sprint-ready objects.

        Returns:
            SprintPlanning: Final structured sprint plan containing all sprints
                with grouped user stories and aggregated effort.

        Logs:
            - Start and completion of sprint generation
            - Number of sprint groups produced by LLM
            - Warning if a story ID is missing in lookup

        Notes:
            - Missing stories are skipped with a warning log
            - Sprint effort is computed as sum of all task estimated hours
            - LLM is used only for grouping, not for final calculations
        """
        logger.info("Starting sprint grouping process.")

        grouping: SprintGrouping = self._call_llm(
            agent_name="SprintGrouperAgent",
            folder_name="backlog_generation",
            prompt_name="sprint_grouper_agent",
            variables={
                "stories_summary": epics
            },
            response_format=SprintGrouping,
        )

        logger.info("LLM produced %d sprint groups.", len(grouping.sprints))

        sprints = []
        for sprint_group in grouping.sprints:
            user_stories = []
            for story_id in sprint_group.story_ids:
                story = story_lookup.get(story_id)
                if not story:
                    logger.warning("Story ID not found: %s", story_id)
                    continue
                user_stories.append(story)

            total_hours = round(
                sum(
                    task.estimated_hours
                    for us in user_stories
                    for task in us.tasks
                ), 2
            )

            sprints.append(Sprint(
                name=sprint_group.name,
                goal=sprint_group.goal,
                total_estimated_hours=total_hours,
                user_stories=user_stories
            ))

        logger.info("Sprint grouping completed. %d sprints built.", len(sprints))
        return SprintPlanning(sprints=sprints)