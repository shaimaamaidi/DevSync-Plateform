"""
Task generator agent.

This module defines the TaskGeneratorAgent, responsible for generating
structured development tasks from user stories using an LLM. It enriches
each user story with actionable technical tasks based on product context
and refined market intelligence.
"""

import logging

from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam

from backend.src.domain.entities.backlog.task import TaskList
from backend.src.domain.entities.backlog.user_story import UserStory
from backend.src.domain.entities.market.refined_market_intelligence import RefinedMarketIntelligenceSummary
from backend.src.domain.entities.product.initial_description import InitialDescription
from backend.src.domain.exceptions.llm_parsing_exception import LLMParsingException
from backend.src.domain.ports.services.backlog_generation.agents.itask_generator import ITaskGenerator
from backend.src.infrastructure.external.backlog_generation.agents.base_agent import BaseAgent


logger = logging.getLogger(__name__)


class TaskGeneratorAgent(BaseAgent, ITaskGenerator):
    """
    LLM-based implementation of ITaskGenerator.

    This agent is responsible for:
    - Generating technical implementation tasks from a user story
    - Enriching tasks using product description and market intelligence
    - Ensuring tasks are granular, actionable, and implementation-ready
    """

    def generate_tasks_by_user_story(
        self,
        user_story: UserStory,
        detailed_description: InitialDescription,
        context: RefinedMarketIntelligenceSummary
    ) -> TaskList:
        """
        Generate a list of tasks for a given user story using an LLM.

        This method transforms a user story into a set of actionable development tasks
        by incorporating product-level context and refined market intelligence, using
        prompt-based LLM reasoning to ensure completeness and relevance, and returning
        a structured TaskList aligned with the user story.

        Args:
            user_story (UserStory): The user story to decompose into tasks.
            detailed_description (InitialDescription): Product-level context.
            context (RefinedMarketIntelligenceSummary): Refined market intelligence context.

        Returns:
            TaskList: Generated list of structured tasks for the user story.
            
        Raises:
            LLMParsingException: May raise underlying LLM or parsing errors from OpenAI client.
        """
        logger.info("Generating tasks for user story: %s.", user_story.title)

        messages = self.prompt_loader.get_messages(
            name="task_generator_agent",
            variables={
                "title": user_story.title,
                "description": user_story.description,
                "overview": detailed_description.product_overview,
                "target_users":  "\n".join(f"- {u}" for u in detailed_description.target_users),
                "core_features": "\n".join(f"- {f}" for f in detailed_description.core_features),
                "business_goals":  "\n".join(f"- {g}" for g in detailed_description.business_goals),
                "summary": detailed_description.summary,
                "technical_constraints":  "\n".join(f"- {c}" for c in detailed_description.constraints),
                "best_practices":  "\n".join(f"- {p}" for p in context.refined_best_practices),
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
                response_format=TaskList,
                temperature=0,
            )

            response = completion.choices[0].message.parsed
            response.user_story_title = user_story.title

            logger.info("Task generation completed for user story: %s.", user_story.title)

            return response
        except Exception as e:
            logger.exception("Task generating failed.")
            raise LLMParsingException(
                agent_name="TaskGeneratorAgent",
                reason=str(e)
            ) from e