"""
Market intelligence summarizer agent.

This module defines the MarketIntelligenceSummarizerAgent, responsible for
summarizing raw product description and optional web results into structured
market intelligence using an LLM.

The agent extracts insights such as market trends, user pain points,
competitor features, and best practices to enrich backlog generation.
"""

import logging

from typing import Optional

from backend.src.domain.entities.market.intelligence import MarketIntelligenceSummary
from backend.src.domain.entities.product.initial_description import InitialDescription
from backend.src.domain.ports.services.backlog_generation.agents.i_market_intelligence_summarizer import \
    IMarketIntelligenceSummarizer
from backend.src.domain.ports.services.prompt_loading.i_prompt_loader import IPromptLoader
from backend.src.infrastructure.external.shared.agents.base_agent import BaseAgent


logger = logging.getLogger(__name__)


class MarketIntelligenceSummarizerAgent(BaseAgent[MarketIntelligenceSummary], IMarketIntelligenceSummarizer):
    """
    LLM-based implementation of IMarketIntelligenceSummarizer.

    This agent is responsible for:
    - Summarizing product description into market intelligence
    - Enriching context using optional web results
    - Extracting structured insights for backlog generation
    """

    def __init__(self, prompt_loader: IPromptLoader):
        """
        Initialize the MarketIntelligenceSummarizerAgent.

        Args:
            prompt_loader (IPromptLoader): Service responsible for loading
                prompt templates used by the agent during LLM interactions.
        """
        super().__init__(prompt_loader)

    def summarize_context(
        self,
        detailed_description: InitialDescription,
        web_result: Optional[str] = None
    ) -> MarketIntelligenceSummary:
        """
        Generate a structured market intelligence summary using an LLM.

        Args:
            detailed_description (InitialDescription): Product description input.
            web_result (Optional[str]): Optional web search results for enrichment.

        Returns:
            MarketIntelligenceSummary: Structured market intelligence summary.

        Raises:
            LLMNetworkException: If a network error occurs while contacting the LLM.
            LLMApiException: If the LLM API returns an error response.
            LLMParsingException: May raise underlying LLM or parsing errors from OpenAI client.
        """
        logger.info("Starting market intelligence summarization process.")

        result = self._call_llm(
            agent_name="MarketIntelligenceSummarizerAgent",
            folder_name="backlog_generation",
            prompt_name="market_intelligence_summarizer_agent",
            variables={
                "overview": detailed_description.product_overview,
                "target_users": "\n".join(f"- {u}" for u in detailed_description.target_users),
                "core_features": "\n".join(f"- {f}" for f in detailed_description.core_features),
                "business_goals": "\n".join(f"- {g}" for g in detailed_description.business_goals),
                "constraints": "\n".join(f"- {c}" for c in detailed_description.constraints),
                "summary": detailed_description.summary,
                "web_result": web_result if web_result else "None",
            },
            response_format=MarketIntelligenceSummary,
        )

        logger.info("Market intelligence summarization completed successfully.")

        return result