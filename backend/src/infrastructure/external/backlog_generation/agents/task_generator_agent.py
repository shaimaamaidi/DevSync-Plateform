"""
Task generator agent.

This module defines the TaskGeneratorAgent, responsible for generating
structured development tasks from user stories using an LLM. It enriches
each user story with actionable technical tasks based on product context
and refined market intelligence.
"""

import logging

from backend.src.domain.entities.backlog.task import TaskList
from backend.src.domain.entities.backlog.user_story import UserStory
from backend.src.domain.entities.market.refined_intelligence import RefinedMarketIntelligenceSummary
from backend.src.domain.entities.product.initial_description import InitialDescription
from backend.src.domain.ports.services.backlog_generation.agents.i_task_generator import ITaskGenerator
from backend.src.domain.ports.services.prompt_loading.i_prompt_loader import IPromptLoader
from backend.src.infrastructure.external.shared.agents.base_agent import BaseAgent


logger = logging.getLogger(__name__)


class TaskGeneratorAgent(BaseAgent[TaskList], ITaskGenerator):
    """
    LLM-based implementation of ITaskGenerator.

    This agent is responsible for:
    - Generating technical implementation tasks from a user story
    - Enriching tasks using product description and market intelligence
    - Ensuring tasks are granular, actionable, and implementation-ready
    """

    def __init__(self, prompt_loader: IPromptLoader):
        """
        Initialize the TaskGeneratorAgent.

        This constructor sets up the agent with the prompt loading service
        used to retrieve LLM templates for task generation.

        The prompt loader is responsible for:
        - Loading task generation prompts
        - Providing structured LLM templates
        - Ensuring consistent task decomposition across user stories

        Args:
            prompt_loader (IPromptLoader): Service responsible for loading
                prompt templates used by the agent during LLM interactions.
        """
        super().__init__(prompt_loader)

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
            LLMNetworkException: If a network error occurs while contacting the LLM.
            LLMApiException: If the LLM API returns an error response.
            LLMParsingException: May raise underlying LLM or parsing errors from OpenAI client.
        """
        logger.info("Generating tasks for user story: %s.", user_story.title)

        result = self._call_llm(
            agent_name="TaskGeneratorAgent",
            folder_name="backlog_generation",
            prompt_name="task_generator_agent",
            variables={
                "title": user_story.title,
                "description": user_story.description,
                "overview": detailed_description.product_overview,
                "target_users": "\n".join(f"- {u}" for u in detailed_description.target_users),
                "core_features": "\n".join(f"- {f}" for f in detailed_description.core_features),
                "business_goals": "\n".join(f"- {g}" for g in detailed_description.business_goals),
                "summary": detailed_description.summary,
                "technical_constraints": "\n".join(f"- {c}" for c in detailed_description.constraints),
                "best_practices": "\n".join(f"- {p}" for p in context.refined_best_practices),
                "enrichment_notes": context.refined_enrichment_notes,
            },
            response_format=TaskList,
        )

        result.user_story_title = user_story.title

        logger.info("Task generation completed for user story: %s.", user_story.title)

        return result