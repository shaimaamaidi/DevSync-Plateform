"""
Epic cleaner agent.

This module defines the EpicCleanerAgent, responsible for validating and
cleaning a generated epic using an LLM. It ensures that the epic structure
is consistent, normalized, and compliant with expected domain rules.
"""

import logging

from backend.src.domain.entities.backlog.structure import EpicBacklog
from backend.src.domain.ports.services.backlog_generation.agents.i_epic_cleaner import IEpicCleaner
from backend.src.domain.ports.services.prompt_loading.i_prompt_loader import IPromptLoader
from backend.src.infrastructure.external.backlog_generation.helpers.backlog_formatter import format_epic
from backend.src.infrastructure.external.shared.agents.base_agent import BaseAgent


logger = logging.getLogger(__name__)


class EpicCleanerAgent(BaseAgent[EpicBacklog], IEpicCleaner):
    """
    LLM-based implementation of IEpicCleaner.

    This agent is responsible for:
    - Cleaning and normalizing generated epic structures
    - Ensuring consistency between epics, user stories, and tasks
    - Removing inconsistencies or invalid structures using LLM reasoning
    """

    def __init__(self, prompt_loader: IPromptLoader):
        """
        Initialize the EpicCleanerAgent.

        Args:
            prompt_loader (IPromptLoader): Service responsible for loading
                prompt templates used by the agent during LLM interactions.
        """
        super().__init__(prompt_loader)

    def clean_epic(self, epic: EpicBacklog) -> EpicBacklog:
        """
        Clean and validate an epic using an LLM.

        The method sends the current epic to the prompt-based LLM pipeline,
        which returns a structured and cleaned version of the epic.

        Args:
            epic (EpicBacklog): The raw or partially generated epic.

        Returns:
            EpicBacklog: The cleaned and normalized epic.

        Raises:
            LLMNetworkException: If a network error occurs while contacting the LLM.
            LLMApiException: If the LLM API returns an error response.
            LLMParsingException: May raise underlying LLM or parsing errors from OpenAI client.
        """
        logger.info("Starting epic cleaning process.")

        result = self._call_llm(
            agent_name="EpicCleanerAgent",
            folder_name="backlog_generation",
            prompt_name="epic_cleaner_agent",
            variables={
                "epic": format_epic(epic)
            },
            response_format=EpicBacklog,
        )

        logger.info("Epic cleaning completed successfully.")

        return result