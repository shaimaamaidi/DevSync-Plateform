"""
Product context builder agent.

This module defines the ProductContextBuilderAgent, responsible for transforming
a raw product description string into a structured InitialDescription object
using an LLM.

The agent extracts and structures key product information such as features,
target users, business goals, and constraints.
"""

import logging

from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam

from backend.src.domain.entities.product.initial_description import InitialDescription
from backend.src.domain.exceptions.llm.llm_parsing_exception import LLMParsingException
from backend.src.domain.ports.services.backlog_generation.agents.iproduct_context_builder import IProductContextBuilder
from backend.src.infrastructure.external.shared.agents.base_agent import BaseAgent


logger = logging.getLogger(__name__)


class ProductContextBuilderAgent(BaseAgent, IProductContextBuilder):
    """
    LLM-based implementation of IProductContextBuilder.

    This agent is responsible for:
    - Structuring raw product descriptions
    - Extracting key product attributes
    - Producing a normalized InitialDescription used across backlog generation
    """

    def build_context(self, description: str) -> InitialDescription:
        """
        Build a structured product context from a raw description.

        The method sends the raw product description to the prompt-based LLM pipeline,
        which returns a structured and normalized representation of the product
        including key elements such as overview, target users, features, goals,
        and constraints.

        Args:
            description (str): Raw product description input.

        Returns:
            InitialDescription: Structured product context.

        Raises:
            LLMParsingException: May raise underlying LLM or parsing errors from OpenAI client.
        """
        logger.info("Starting product context building process.")

        messages = self.prompt_loader.get_messages(
            folder_name="backlog_generation",
            name="product_context_builder_agent",
            variables={
                "description": description,
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
                response_format=InitialDescription,
                temperature=0,
            )

            logger.info("Product context building completed successfully.")

            return completion.choices[0].message.parsed
        except Exception as e:
            logger.exception("Product context building failed.")
            raise LLMParsingException(
                agent_name="ProductContextBuilderAgent",
                reason=str(e)
            ) from e