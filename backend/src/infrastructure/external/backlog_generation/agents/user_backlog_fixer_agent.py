"""
User backlog fixer agent.

This module defines the UserBacklogFixerAgent, responsible for validating and
correcting a user-provided backlog by comparing it against a reference backlog
using an LLM. It ensures structural consistency, completeness, and alignment
with the expected domain model.
"""

import logging

from backend.src.domain.entities.backlog.structure import BacklogStructure
from backend.src.domain.entities.backlog.validation import BacklogValidation
from backend.src.domain.ports.services.backlog_generation.agents.i_user_backlog_fixer import IUserBacklogFixer
from backend.src.domain.ports.services.prompt_loading.i_prompt_loader import IPromptLoader
from backend.src.infrastructure.external.shared.agents.base_agent import BaseAgent
from backend.src.infrastructure.external.backlog_generation.helpers.backlog_formatter import format_backlog


logger = logging.getLogger(__name__)


class UserBacklogFixerAgent(BaseAgent[BacklogValidation], IUserBacklogFixer):
    """
    LLM-based implementation of IUserBacklogFixer.

    This agent is responsible for:
    - Comparing a user-provided backlog with a reference backlog
    - Detecting inconsistencies, missing elements, or structural issues
    - Producing a validated and corrected backlog representation
    """

    def __init__(self, prompt_loader: IPromptLoader):
        """
        Initialize the UserBacklogFixerAgent.

        Args:
            prompt_loader (IPromptLoader): Service responsible for loading
                prompt templates used by the agent during LLM interactions.
        """
        super().__init__(prompt_loader)

    def fix_user_backlog(
            self,
            backlog_reference: BacklogStructure,
            backlog_to_validate: BacklogStructure,
    ) -> BacklogValidation:
        """
        Validate and fix a user backlog by comparing it with a reference backlog.

        The method sends both the reference backlog and the user-modified backlog
        to the prompt-based LLM pipeline, which returns a validated and corrected
        version of the backlog along with detected issues.

        Args:
            backlog_reference (BacklogStructure): The expected/reference backlog structure.
            backlog_to_validate (BacklogStructure): The user-provided backlog to validate.

        Returns:
            BacklogValidation: Validation result including corrected backlog and issues.

        Raises:
            LLMNetworkException: If a network error occurs while contacting the LLM.
            LLMApiException: If the LLM API returns an error response.
            LLMParsingException: May raise underlying LLM or parsing errors from OpenAI client.
        """
        logger.info("Starting user backlog validation process.")

        result = self._call_llm(
            agent_name="UserBacklogFixerAgent",
            folder_name="backlog_generation",
            prompt_name="user_backlog_fixer_agent",
            variables={
                "reference_backlog": format_backlog(backlog_reference),
                "user_backlog": format_backlog(backlog_to_validate),
            },
            response_format=BacklogValidation,
        )

        logger.info("User backlog validation completed successfully.")

        return result