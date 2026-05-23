"""
Sprint planner agent.

This module defines the SprintPlannerAgent, responsible for generating sprint
planning structures from a structured backlog using an LLM. It transforms a
prioritized backlog into time-based sprint distributions suitable for agile planning.
"""

import logging

from backend.src.domain.entities.backlog.structure import BacklogStructure
from backend.src.domain.entities.sprint.planning import SprintPlanning
from backend.src.domain.ports.services.backlog_generation.agents.isprint_planner import ISprintPlanner
from backend.src.infrastructure.external.shared.agents.base_agent import BaseAgent
from backend.src.infrastructure.external.backlog_generation.helpers.backlog_formatter import format_backlog


logger = logging.getLogger(__name__)


class SprintPlannerAgent(BaseAgent, ISprintPlanner):
    """
    LLM-based implementation of ISprintPlanner.

    This agent is responsible for:
    - Transforming a structured backlog into sprint plans
    - Distributing epics/user stories into time-boxed iterations
    - Ensuring realistic sprint allocation based on backlog complexity
    """

    def generate_sprints(self, backlog: BacklogStructure) -> SprintPlanning:
        """
        Generate sprint planning from a backlog using an LLM.

        This method sends the formatted backlog to the LLM prompt pipeline and
        returns a structured sprint planning output.

        Args:
            backlog (BacklogStructure): The prioritized and cleaned backlog.

        Returns:
            SprintPlanning: The generated sprint plan structure.

        Raises:
            LLMNetworkException: If a network error occurs while contacting the LLM.
            LLMApiException: If the LLM API returns an error response.
            LLMParsingException: May raise underlying LLM or parsing errors from OpenAI client.
        """
        logger.info("Starting sprint planning generation.")

        result = self._call_llm(
            agent_name="SprintPlannerAgent",
            folder_name="backlog_generation",
            prompt_name="sprint_planner_agent",
            variables={
                "backlog": format_backlog(backlog),
            },
            response_format=SprintPlanning,
        )

        logger.info("Sprint planning generation completed successfully.")

        return result