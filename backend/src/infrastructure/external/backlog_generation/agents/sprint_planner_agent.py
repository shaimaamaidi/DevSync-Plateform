"""
Sprint planner agent.

This module defines the SprintPlannerAgent, responsible for generating sprint
planning structures from a structured backlog using an LLM. It transforms a
prioritized backlog into time-based sprint distributions suitable for agile planning.
"""

import logging

from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam

from backend.src.domain.entities.backlog.backlog_structure import BacklogStructure
from backend.src.domain.entities.sprint.sprint_planning import SprintPlanning
from backend.src.domain.exceptions.llm.llm_parsing_exception import LLMParsingException
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
            LLMParsingException: May raise underlying LLM or parsing errors from OpenAI client.
        """
        logger.info("Starting sprint planning generation.")

        messages = self.prompt_loader.get_messages(
            name="sprint_planner_agent",
            variables={
                "backlog": format_backlog(backlog),
            }
        )

        messages = [
            ChatCompletionSystemMessageParam(role="system", content=messages["system"]),
            ChatCompletionUserMessageParam(role="user", content=messages["user"])
        ]

        try:
            completion = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=messages,
                response_format=SprintPlanning,
                temperature=0,
            )

            logger.info("Sprint planning generation completed successfully.")

            return completion.choices[0].message.parsed
        except Exception as e:
            logger.exception("Sprint planning failed.")
            raise LLMParsingException(
                agent_name="SprintPlannerAgent",
                reason=str(e)
            ) from e