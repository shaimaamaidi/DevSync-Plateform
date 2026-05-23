"""
Epic generator agent.

This module defines the EpicGeneratorAgent, responsible for generating
product epics from a detailed product description and enriched market
intelligence using an LLM.

The agent transforms high-level product inputs into structured epics
that serve as the foundation of backlog generation.
"""

import logging

from backend.src.domain.entities.backlog.epic import EpicList
from backend.src.domain.entities.market.refined_intelligence import RefinedMarketIntelligenceSummary
from backend.src.domain.entities.product.initial_description import InitialDescription
from backend.src.domain.ports.services.backlog_generation.agents.iepic_generator import IEpicGenerator
from backend.src.infrastructure.external.shared.agents.base_agent import BaseAgent


logger = logging.getLogger(__name__)


class EpicGeneratorAgent(BaseAgent, IEpicGenerator):
    """
    LLM-based implementation of IEpicGenerator.

    This agent is responsible for:
    - Generating epics from product descriptions
    - Enriching epics using market intelligence context
    - Structuring high-level product capabilities into backlog epics
    """

    def generate_epics(
        self,
        detailed_description: InitialDescription,
        context: RefinedMarketIntelligenceSummary
    ) -> EpicList:
        """
        Generate product epics using an LLM.

        The method combines product description and market intelligence
        to produce structured epics that define the product roadmap.

        Args:
            detailed_description (InitialDescription): Product description including features,
                goals, and users.
            context (RefinedMarketIntelligenceSummary): Market intelligence enrichment data.

        Returns:
            EpicList: Generated list of structured epics.

        Raises:
            LLMNetworkException: If a network error occurs while contacting the LLM.
            LLMApiException: If the LLM API returns an error response.
            LLMParsingException: May raise underlying LLM or parsing errors from OpenAI client.
        """
        logger.info("Starting epic generation process.")

        result = self._call_llm(
            agent_name="EpicGeneratorAgent",
            folder_name="backlog_generation",
            prompt_name="epic_generator_agent",
            variables={
                "overview": detailed_description.product_overview,
                "target_users": "\n".join(f"- {u}" for u in detailed_description.target_users),
                "core_features": "\n".join(f"- {f}" for f in detailed_description.core_features),
                "business_goals": "\n".join(f"- {g}" for g in detailed_description.business_goals),
                "summary": detailed_description.summary,
                "market_trends": context.refined_market_trends,
                "competitor_features": context.refined_competitor_features,
                "user_pain_points": context.refined_user_pain_points,
                "best_practices": context.refined_best_practices,
                "enrichment_notes": context.refined_enrichment_notes,
            },
            response_format=EpicList,
        )

        logger.info("Epic generation completed successfully.")

        return result
