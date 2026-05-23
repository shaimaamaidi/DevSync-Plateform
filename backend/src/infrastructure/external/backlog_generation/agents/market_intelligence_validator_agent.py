"""
Market intelligence validator agent.

This module defines the MarketIntelligenceValidatorAgent, responsible for
validating and refining market intelligence data using an LLM. It ensures that
the generated market intelligence is consistent, relevant, and aligned with the
product description.
"""

import logging

from backend.src.domain.entities.market.intelligence import MarketIntelligenceSummary
from backend.src.domain.entities.market.refined_intelligence import RefinedMarketIntelligenceSummary
from backend.src.domain.entities.product.initial_description import InitialDescription
from backend.src.domain.ports.services.backlog_generation.agents.imarket_intelligence_validator import \
    IMarketIntelligenceValidator
from backend.src.infrastructure.external.shared.agents.base_agent import BaseAgent


logger = logging.getLogger(__name__)


class MarketIntelligenceValidatorAgent(BaseAgent, IMarketIntelligenceValidator):
    """
    LLM-based implementation of IMarketIntelligenceValidator.

    This agent is responsible for:
    - Validating market intelligence against product description
    - Ensuring consistency between product context and market insights
    - Refining and normalizing market intelligence using LLM reasoning
    """

    def validate_context(
        self,
        detailed_description: InitialDescription,
        context: MarketIntelligenceSummary
    ) -> RefinedMarketIntelligenceSummary:
        """
        Validate and refine market intelligence using an LLM.

        The method sends the product description and market intelligence to the
        prompt-based LLM pipeline, which returns a structured and validated version
        of the market intelligence.

        Args:
            detailed_description (InitialDescription): The structured product description.
            context (MarketIntelligenceSummary): The generated or raw market intelligence.

        Returns:
            RefinedMarketIntelligenceSummary: The validated and refined market intelligence.

        Raises:
            LLMNetworkException: If a network error occurs while contacting the LLM.
            LLMApiException: If the LLM API returns an error response.
            LLMParsingException: May raise underlying LLM or parsing errors from OpenAI client.
        """
        logger.info("Validating market intelligence with LLM.")

        result = self._call_llm(
            agent_name="MarketIntelligenceValidatorAgent",
            folder_name="backlog_generation",
            prompt_name="market_intelligence_validator_agent",
            variables={
                "overview": detailed_description.product_overview,
                "target_users": "\n".join(f"- {u}" for u in detailed_description.target_users),
                "core_features": "\n".join(f"- {f}" for f in detailed_description.core_features),
                "business_goals": "\n".join(f"- {g}" for g in detailed_description.business_goals),
                "constraints": "\n".join(f"- {c}" for c in detailed_description.constraints),
                "summary": detailed_description.summary,
                "market_trends": context.market_trends,
                "competitor_features": context.competitor_features,
                "user_pain_points": context.user_pain_points,
                "best_practices": context.best_practices,
                "enrichment_notes": context.enrichment_notes,
            },
            response_format=RefinedMarketIntelligenceSummary,
        )

        logger.info("Market intelligence validated successfully.")

        return result