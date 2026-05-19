"""
User story generator agent.

This module defines the UserStoryGeneratorAgent, responsible for generating
structured user stories from a given epic using an LLM. It enriches each epic
with user stories based on product context and refined market intelligence.
"""

import logging

from openai import APIConnectionError, APIStatusError
from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam

from backend.src.domain.entities.backlog.epic import Epic
from backend.src.domain.entities.backlog.user_story import UserStoryList
from backend.src.domain.entities.market.refined_intelligence import RefinedMarketIntelligenceSummary
from backend.src.domain.entities.product.initial_description import InitialDescription
from backend.src.domain.exceptions.llm.llm_api_exception import LLMApiException
from backend.src.domain.exceptions.llm.llm_network_exception import LLMNetworkException
from backend.src.domain.exceptions.llm.llm_parsing_exception import LLMParsingException
from backend.src.domain.ports.services.backlog_generation.agents.iuser_strory_generator import IUserStoryGenerator
from backend.src.infrastructure.external.shared.agents.base_agent import BaseAgent


logger = logging.getLogger(__name__)


class UserStoryGeneratorAgent(BaseAgent, IUserStoryGenerator):
    """
    LLM-based implementation of IUserStoryGenerator.

    This agent is responsible for:
    - Generating user stories from a given epic
    - Ensuring alignment with product goals and market insights
    - Structuring user stories in a consistent domain format
    """

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

        messages = self.prompt_loader.get_messages(
            folder_name="backlog_generation",
            name="user_story_generator_agent",
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
                response_format=UserStoryList,
                temperature=0,
            )

            response = completion.choices[0].message.parsed
            response.epic_title = epic.title

            logger.info("User story generation completed for epic: %s.", epic.title)

            return response

        except APIConnectionError as e:
            logger.exception("Network error contacting LLM in UserStoryGeneratorAgent: reason=%s.", str(e))
            raise LLMNetworkException() from e

        except APIStatusError as e:
            logger.exception("LLM API error in UserStoryGeneratorAgent: status=%d.", e.status_code)
            raise LLMApiException() from e

        except Exception as e:
            logger.exception("User story generating failed: reason=%s.", str(e))
            raise LLMParsingException() from e