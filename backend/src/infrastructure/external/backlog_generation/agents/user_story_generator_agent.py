"""
User story generator agent.

This module defines the UserStoryGeneratorAgent, responsible for generating
structured user stories from a given epic using an LLM. It enriches each epic
with user stories based on product context and refined market intelligence.
"""

import logging

from backend.src.domain.entities.backlog.epic import Epic
from backend.src.domain.entities.backlog.user_story import UserStoryList
from backend.src.domain.entities.market.refined_intelligence import RefinedMarketIntelligenceSummary
from backend.src.domain.entities.product.initial_description import InitialDescription
from backend.src.domain.ports.services.backlog_generation.agents.iuser_strory_generator import IUserStoryGenerator
from backend.src.domain.ports.services.iprompt_loader import IPromptLoader
from backend.src.infrastructure.external.shared.agents.base_agent import BaseAgent


logger = logging.getLogger(__name__)


class UserStoryGeneratorAgent(BaseAgent[UserStoryList], IUserStoryGenerator):
    """
    LLM-based implementation of IUserStoryGenerator.

    This agent is responsible for:
    - Generating user stories from a given epic
    - Ensuring alignment with product goals and market insights
    - Structuring user stories in a consistent domain format
    """

    def __init__(self, prompt_loader: IPromptLoader):
        """
        Initialize the UserStoryGeneratorAgent.

        Args:
            prompt_loader (IPromptLoader): Service responsible for loading
                prompt templates used by the agent during LLM interactions.
        """
        super().__init__(prompt_loader)

    def generate_user_stories_by_epic(
        self,
        epic: Epic,
        detailed_description: InitialDescription,
        context: RefinedMarketIntelligenceSummary
    ) -> UserStoryList:
        """
        Generate user stories for a given epic using an LLM.

        This method breaks down a given epic into structured user stories by leveraging
        product context and refined market intelligence. It uses an LLM to ensure that
        the generated stories are aligned with business goals, user needs, and market insights.

        Args:
            epic (Epic): The epic to decompose into user stories.
            detailed_description (InitialDescription): Product-level context.
            context (RefinedMarketIntelligenceSummary): Refined market intelligence context.

        Returns:
            UserStoryList: Generated list of user stories for the epic.
            
        Raises:
            LLMNetworkException: If a network error occurs while contacting the LLM.
            LLMApiException: If the LLM API returns an error response.
            LLMParsingException: May raise underlying LLM or parsing errors from OpenAI client.
        """
        logger.info("Generating user stories for epic: %s.", epic.title)

        result = self._call_llm(
            agent_name="UserStoryGeneratorAgent",
            folder_name="backlog_generation",
            prompt_name="user_story_generator_agent",
            variables={
                "title": epic.title,
                "description": epic.description,
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
            response_format=UserStoryList,
        )

        result.epic_title = epic.title

        logger.info("User story generation completed for epic: %s.", epic.title)

        return result
