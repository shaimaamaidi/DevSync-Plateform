"""
Product context builder agent.

This module defines the ProductContextBuilderAgent, responsible for transforming
a raw product description string into a structured InitialDescription object
using an LLM.

The agent extracts and structures key product information such as features,
target users, business goals, and constraints.
"""

import logging

from backend.src.domain.entities.product.initial_description import InitialDescription
from backend.src.domain.ports.services.backlog_generation.agents.iproduct_context_builder import IProductContextBuilder
from backend.src.domain.ports.services.iprompt_loader import IPromptLoader
from backend.src.infrastructure.external.shared.agents.base_agent import BaseAgent


logger = logging.getLogger(__name__)


class ProductContextBuilderAgent(BaseAgent[InitialDescription], IProductContextBuilder):
    """
    LLM-based implementation of IProductContextBuilder.

    This agent is responsible for:
    - Structuring raw product descriptions
    - Extracting key product attributes
    - Producing a normalized InitialDescription used across backlog generation
    """

    def __init__(self, prompt_loader: IPromptLoader):
        """
        Initialize the ProductContextBuilderAgent.

        Args:
            prompt_loader (IPromptLoader): Service responsible for loading
                prompt templates used by the agent during LLM interactions.
        """
        super().__init__(prompt_loader)

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
            LLMNetworkException: If a network error occurs while contacting the LLM.
            LLMApiException: If the LLM API returns an error response.
            LLMParsingException: May raise underlying LLM or parsing errors from OpenAI client.
        """
        logger.info("Starting product context building process.")

        result = self._call_llm(
            agent_name="ProductContextBuilderAgent",
            folder_name="backlog_generation",
            prompt_name="product_context_builder_agent",
            variables={
                "description": description,
            },
            response_format=InitialDescription,
        )

        logger.info("Product context building completed successfully.")

        return result