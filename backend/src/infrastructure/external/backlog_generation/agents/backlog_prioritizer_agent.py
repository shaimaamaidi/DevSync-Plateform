"""
Backlog prioritizer agent.

This module defines the BacklogPrioritizerAgent, responsible for prioritizing
a generated backlog using an LLM. It reorganizes epics, user stories, and tasks
based on business value, dependencies, and product strategy.
"""

import logging

from backend.src.domain.entities.backlog.structure import BacklogStructure
from backend.src.domain.ports.services.backlog_generation.agents.ibacklog_prioritizer import IBacklogPrioritizer
from backend.src.domain.ports.services.iprompt_loader import IPromptLoader
from backend.src.infrastructure.external.shared.agents.base_agent import BaseAgent
from backend.src.infrastructure.external.backlog_generation.helpers.backlog_formatter import format_backlog


logger = logging.getLogger(__name__)


class BacklogPrioritizerAgent(BaseAgent[BacklogStructure], IBacklogPrioritizer):
    """
    LLM-based implementation of IBacklogPrioritizer.

    This agent is responsible for:
    - Prioritizing backlog items based on business value and dependencies
    - Reordering epics, user stories, and tasks
    - Ensuring alignment with product strategy using LLM reasoning
    """

    def __init__(self, prompt_loader: IPromptLoader):
        """
        Initialize the BacklogPrioritizerAgent.

        Args:
            prompt_loader (IPromptLoader): Service responsible for loading
                prompt templates used by the agent during LLM interactions.
        """
        super().__init__(prompt_loader)

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
            LLMNetworkException: If a network error occurs while contacting the LLM.
            LLMApiException: If the LLM API returns an error response.
            LLMParsingException: May raise underlying LLM or parsing errors from OpenAI client.
        """
        logger.info("Starting backlog prioritization process.")

        result = self._call_llm(
            agent_name="BacklogPrioritizerAgent",
            folder_name="backlog_generation",
            prompt_name="backlog_prioritizer_agent",
            variables={
                "backlog": format_backlog(backlog),
            },
            response_format=BacklogStructure,
        )

        logger.info("Backlog prioritization completed successfully.")

        return result
