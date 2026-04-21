"""
Backlog prioritizer agent.

This module defines the BacklogPrioritizerAgent, responsible for prioritizing
a generated backlog using an LLM. It reorganizes epics, user stories, and tasks
based on business value, dependencies, and product strategy.
"""

import logging

from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam

from backend.src.domain.entities.backlog.backlog_structure import BacklogStructure
from backend.src.domain.exceptions.llm_parsing_exception import LLMParsingException
from backend.src.domain.ports.services.backlog_generation.agents.ibacklog_prioritizer import IBacklogPrioritizer
from backend.src.infrastructure.external.backlog_generation.agents.base_agent import BaseAgent
from backend.src.infrastructure.external.backlog_generation.helpers.backlog_formatter import format_backlog


logger = logging.getLogger(__name__)


class BacklogPrioritizerAgent(BaseAgent, IBacklogPrioritizer):
    """
    LLM-based implementation of IBacklogPrioritizer.

    This agent is responsible for:
    - Prioritizing backlog items based on business value and dependencies
    - Reordering epics, user stories, and tasks
    - Ensuring alignment with product strategy using LLM reasoning
    """

    def prioritize(self, backlog: BacklogStructure) -> BacklogStructure:
        """
        Prioritize a backlog using an LLM.

        The method sends the backlog to the LLM, which returns a reordered
        and prioritized version of the backlog structure.

        Args:
            backlog (BacklogStructure): The raw backlog structure.

        Returns:
            BacklogStructure: The prioritized backlog structure.

        Raises:
            LLMParsingException: May raise underlying LLM or parsing errors from OpenAI client.
        """
        logger.info("Starting backlog prioritization process.")

        messages = self.prompt_loader.get_messages(
            name="backlog_prioritizer_agent",
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
                response_format=BacklogStructure,
                temperature=0,
            )

            logger.info("Backlog prioritization completed successfully.")

            return completion.choices[0].message.parsed
        except Exception as e:
            logger.exception("Backlog prioritizing failed.")
            raise LLMParsingException(
                agent_name="BacklogPrioritizerAgent",
                reason=str(e)
            ) from e