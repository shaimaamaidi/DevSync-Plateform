"""
Service port for task generation.

This module defines the ITaskGenerator interface, which specifies operations for generating
detailed implementation tasks from a user story enriched with product context and market intelligence.
"""

from abc import ABC, abstractmethod

from backend.src.domain.entities.backlog.task import TaskList
from backend.src.domain.entities.backlog.user_story import UserStory
from backend.src.domain.entities.market.refined_intelligence import RefinedMarketIntelligenceSummary
from backend.src.domain.entities.product.initial_description import InitialDescription


class ITaskGenerator(ABC):
    """
    Define task generation behavior required by the application.

    This interface is responsible for breaking down a user story into actionable tasks,
    using both the product context and refined market intelligence to ensure relevance
    and completeness.
    """

    @abstractmethod
    def generate_tasks_by_user_story(
        self,
        user_story: UserStory,
        detailed_description: InitialDescription,
        context: RefinedMarketIntelligenceSummary,
    ) -> TaskList:
        """
        Generate a list of tasks for a given user story.

        Args:
            user_story (UserStory): The user story to decompose into tasks.
            detailed_description (InitialDescription): Structured product context.
            context (RefinedMarketIntelligenceSummary): Refined market intelligence context.

        Returns:
            TaskList: Generated tasks grouped under the given user story.
        """
        pass