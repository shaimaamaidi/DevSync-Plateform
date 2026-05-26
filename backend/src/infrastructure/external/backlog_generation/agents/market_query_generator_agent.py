"""
Market query generator agent.

This module defines the MarketQueryGeneratorAgent, responsible for generating
search queries from a product description using an LLM.

The agent transforms product context into structured search queries used
for web exploration and market intelligence enrichment.
"""

import logging

from backend.src.domain.entities.market.query import QueryGeneration
from backend.src.domain.entities.product.initial_description import InitialDescription
from backend.src.domain.ports.services.backlog_generation.agents.i_market_query_generator import IMarketQueryGenerator
from backend.src.domain.ports.services.prompt_loading.i_prompt_loader import IPromptLoader
from backend.src.infrastructure.external.shared.agents.base_agent import BaseAgent


logger = logging.getLogger(__name__)


class MarketQueryGeneratorAgent(BaseAgent[QueryGeneration], IMarketQueryGenerator):
    """
    LLM-based implementation of IMarketQueryGenerator.

    This agent is responsible for:
    - Generating search queries from product descriptions
    - Transforming business context into web-searchable intents
    - Supporting market intelligence enrichment workflows
    """

    def __init__(self, prompt_loader: IPromptLoader):
        """
        Initialize the MarketQueryGeneratorAgent.

        Args:
            prompt_loader (IPromptLoader): Service responsible for loading
                prompt templates used by the agent during LLM interactions.
        """
        super().__init__(prompt_loader)

    def generate_queries(self, detailed_description: InitialDescription) -> QueryGeneration:
        """
        Generate market search queries using an LLM.

        The method sends the product description to the prompt-based LLM pipeline,
        which returns a structured set of search queries tailored for market
        analysis and data collection.

        Args:
            detailed_description (InitialDescription): Product description input.

        Returns:
            QueryGeneration: Structured list of generated search queries.

        Raises:
            LLMNetworkException: If a network error occurs while contacting the LLM.
            LLMApiException: If the LLM API returns an error response.
            LLMParsingException: May raise underlying LLM or parsing errors from OpenAI client.
        """
        logger.info("Starting market query generation process.")

        result = self._call_llm(
            agent_name="MarketQueryGeneratorAgent",
            folder_name="backlog_generation",
            prompt_name="market_query_generator_agent",
            variables={
                "overview": detailed_description.product_overview,
                "target_users": "\n".join(f"- {u}" for u in detailed_description.target_users),
                "core_features": "\n".join(f"- {f}" for f in detailed_description.core_features),
                "business_goals": "\n".join(f"- {g}" for g in detailed_description.business_goals),
                "constraints": "\n".join(f"- {c}" for c in detailed_description.constraints),
                "summary": detailed_description.summary,
            },
            response_format=QueryGeneration,
        )

        logger.info("Market query generation completed successfully.")

        return result

