"""
Backlog cleaner agent.

This module defines the BacklogCleanerAgent, responsible for validating and
cleaning a generated backlog using an LLM. It ensures that the backlog structure
is consistent, normalized, and compliant with expected domain rules.
"""

import logging

from openai import APIConnectionError, APIStatusError
from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam

from backend.src.domain.entities.backlog.structure import BacklogStructure
from backend.src.domain.exceptions.llm.llm_api_exception import LLMApiException
from backend.src.domain.exceptions.llm.llm_network_exception import LLMNetworkException
from backend.src.domain.exceptions.llm.llm_parsing_exception import LLMParsingException
from backend.src.domain.ports.services.backlog_generation.agents.ibacklog_cleaner import IBacklogCleaner
from backend.src.infrastructure.external.shared.agents.base_agent import BaseAgent
from backend.src.infrastructure.external.backlog_generation.helpers.backlog_formatter import format_backlog


logger = logging.getLogger(__name__)


class BacklogCleanerAgent(BaseAgent, IBacklogCleaner):
    """
    LLM-based implementation of IBacklogCleaner.

    This agent is responsible for:
    - Cleaning and normalizing generated backlog structures
    - Ensuring consistency between epics, user stories, and tasks
    - Removing inconsistencies or invalid structures using LLM reasoning
    """

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

        messages = self.prompt_loader.get_messages(
            folder_name="backlog_generation",
            name="backlog_cleaner_agent",
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

            logger.info("Backlog cleaning completed successfully.")

            return completion.choices[0].message.parsed

        except APIConnectionError as e:
            logger.exception("Network error contacting LLM in BacklogCleanerAgent: reason=%s.", str(e))
            raise LLMNetworkException() from e

        except APIStatusError as e:
            logger.exception("LLM API error in BacklogCleanerAgent: status=%d.", e.status_code)
            raise LLMApiException() from e

        except Exception as e:
            logger.exception("Backlog cleaning failed: reason=%s.", str(e))
            raise LLMParsingException() from e