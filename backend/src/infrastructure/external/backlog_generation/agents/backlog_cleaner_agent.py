"""
Backlog cleaner agent.

This module defines the BacklogCleanerAgent, responsible for validating and
cleaning a generated backlog using an LLM. It ensures that the backlog structure
is consistent, normalized, and compliant with expected domain rules.
"""

import logging

from backend.src.domain.entities.backlog.structure import BacklogStructure
from backend.src.domain.ports.services.backlog_generation.agents.ibacklog_cleaner import IBacklogCleaner
from backend.src.domain.ports.services.iprompt_loader import IPromptLoader
from backend.src.infrastructure.external.shared.agents.base_agent import BaseAgent
from backend.src.infrastructure.external.backlog_generation.helpers.backlog_formatter import format_backlog


logger = logging.getLogger(__name__)


class BacklogCleanerAgent(BaseAgent[BacklogStructure], IBacklogCleaner):
    """
    LLM-based implementation of IBacklogCleaner.

    This agent is responsible for:
    - Cleaning and normalizing generated backlog structures
    - Ensuring consistency between epics, user stories, and tasks
    - Removing inconsistencies or invalid structures using LLM reasoning
    """

    def __init__(self, prompt_loader: IPromptLoader):
        """
        Initialize the BacklogCleanerAgent.

        Args:
            prompt_loader (IPromptLoader): Service responsible for loading
                prompt templates used by the agent during LLM interactions.
        """
        super().__init__(prompt_loader)

    def clean_backlog(self, backlog: BacklogStructure) -> BacklogStructure:
        """
        Clean and validate a backlog using an LLM.

        The method sends the current backlog to the prompt-based LLM pipeline,
        which returns a structured and cleaned version of the backlog.

        Args:
            backlog (BacklogStructure): The raw or partially generated backlog.

        Returns:
            BacklogStructure: The cleaned and normalized backlog.

        Raises:
            LLMNetworkException: If a network error occurs while contacting the LLM.
            LLMApiException: If the LLM API returns an error response.
            LLMParsingException: May raise underlying LLM or parsing errors from OpenAI client.
        """
        logger.info("Starting backlog cleaning process.")

        result = self._call_llm(
            agent_name="BacklogCleanerAgent",
            folder_name="backlog_generation",
            prompt_name="backlog_cleaner_agent",
            variables={
                "backlog": format_backlog(backlog)
            },
            response_format=BacklogStructure,
        )

        logger.info("Backlog cleaning completed successfully.")

        return result