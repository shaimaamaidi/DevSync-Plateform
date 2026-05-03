"""
User backlog fixer agent.

This module defines the UserBacklogFixerAgent, responsible for validating and
correcting a user-provided backlog by comparing it against a reference backlog
using an LLM. It ensures structural consistency, completeness, and alignment
with the expected domain model.
"""

import logging

from openai import APIConnectionError, APIStatusError
from openai.types.chat import (
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)

from backend.src.domain.entities.backlog.structure import BacklogStructure
from backend.src.domain.entities.backlog.validation import BacklogValidation
from backend.src.domain.exceptions.llm.llm_api_exception import LLMApiException
from backend.src.domain.exceptions.llm.llm_network_exception import LLMNetworkException
from backend.src.domain.exceptions.llm.llm_parsing_exception import LLMParsingException
from backend.src.domain.ports.services.backlog_generation.agents.iuser_backlog_fixer import IUserBacklogFixer
from backend.src.infrastructure.external.shared.agents.base_agent import BaseAgent
from backend.src.infrastructure.external.backlog_generation.helpers.backlog_formatter import format_backlog


logger = logging.getLogger(__name__)


class UserBacklogFixerAgent(BaseAgent, IUserBacklogFixer):
    """
    LLM-based implementation of IUserBacklogFixer.

    This agent is responsible for:
    - Comparing a user-provided backlog with a reference backlog
    - Detecting inconsistencies, missing elements, or structural issues
    - Producing a validated and corrected backlog representation
    """

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

        messages = self.prompt_loader.get_messages(
            folder_name="backlog_generation",
            name="user_backlog_fixer_agent",
            variables={
                "reference_backlog": format_backlog(backlog_reference),
                "user_backlog": format_backlog(backlog_to_validate),
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
                response_format=BacklogValidation,
                temperature=0,
            )

            logger.info("User backlog validation completed successfully.")

            return completion.choices[0].message.parsed

        except APIConnectionError as e:
            logger.exception("Network error contacting LLM in UserBacklogFixerAgent.")
            raise LLMNetworkException(
                agent_name="UserBacklogFixerAgent",
                reason=str(e)
            ) from e

        except APIStatusError as e:
            logger.exception("LLM API error in UserBacklogFixerAgent: status=%d.", e.status_code)
            raise LLMApiException(
                agent_name="UserBacklogFixerAgent",
                status_code=e.status_code,
                reason=e.message
            ) from e

        except Exception as e:
            logger.exception("User backlog fixing failed.")
            raise LLMParsingException(
                agent_name="UserBacklogFixerAgent",
                reason=str(e)
            ) from e