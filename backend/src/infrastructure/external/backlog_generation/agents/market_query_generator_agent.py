"""
Market query generator agent.

This module defines the MarketQueryGeneratorAgent, responsible for generating
search queries from a product description using an LLM.

The agent transforms product context into structured search queries used
for web exploration and market intelligence enrichment.
"""

import logging

from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam

from backend.src.domain.entities.market.query import QueryGeneration
from backend.src.domain.entities.product.initial_description import InitialDescription
from backend.src.domain.exceptions.llm.llm_parsing_exception import LLMParsingException
from backend.src.domain.ports.services.backlog_generation.agents.imarket_query_generator import IMarketQueryGenerator
from backend.src.infrastructure.external.backlog_generation.agents.base_agent import BaseAgent


logger = logging.getLogger(__name__)


class MarketQueryGeneratorAgent(BaseAgent, IMarketQueryGenerator):
    """
    LLM-based implementation of IMarketQueryGenerator.

    This agent is responsible for:
    - Generating search queries from product descriptions
    - Transforming business context into web-searchable intents
    - Supporting market intelligence enrichment workflows
    """

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
            LLMParsingException: May raise underlying LLM or parsing errors from OpenAI client.
        """
        logger.info("Starting market query generation process.")

        messages = self.prompt_loader.get_messages(
            name="market_query_generator_agent",
            variables={
                "overview": detailed_description.product_overview,
                "target_users": "\n".join(f"- {u}" for u in detailed_description.target_users),
                "core_features": "\n".join(f"- {f}" for f in detailed_description.core_features),
                "business_goals": "\n".join(f"- {g}" for g in detailed_description.business_goals),
                "constraints": "\n".join(f"- {c}" for c in detailed_description.constraints),
                "summary": detailed_description.summary,
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
                response_format=QueryGeneration,
                temperature=0,
            )

            logger.info("Market query generation completed successfully.")

            return completion.choices[0].message.parsed
        except Exception as e:
            logger.exception("Market query generating failed.")
            raise LLMParsingException(
                agent_name="MarketQueryGeneratorAgent",
                reason=str(e)
            ) from e
