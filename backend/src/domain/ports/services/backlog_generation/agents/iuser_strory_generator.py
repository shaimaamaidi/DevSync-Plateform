"""
Service port for user story generation.

This module defines the IUserStoryGenerator interface, which specifies operations for generating
user stories from an epic using product context and refined market intelligence.
"""

from abc import ABC, abstractmethod

from backend.src.domain.entities.backlog.epic import Epic
from backend.src.domain.entities.backlog.user_story import UserStoryList
from backend.src.domain.entities.market.refined_market_intelligence import RefinedMarketIntelligenceSummary
from backend.src.domain.entities.product.initial_description import InitialDescription


class IUserStoryGenerator(ABC):
    """
    Define user story generation behavior required by the application.

    This interface is responsible for transforming a given epic into a set of user stories,
    using both the product description and refined market intelligence to ensure relevance,
    completeness, and business alignment.
    """

    @abstractmethod
    def generate_user_stories_by_epic(
        self,
        epic: Epic,
        detailed_description: InitialDescription,
        context: RefinedMarketIntelligenceSummary,
    ) -> UserStoryList:
        """
        Generate user stories for a given epic.

        Args:
            epic (Epic): The epic to decompose into user stories.
            detailed_description (InitialDescription): Structured product context.
            context (RefinedMarketIntelligenceSummary): Refined market intelligence context.

        Returns:
            UserStoryList: Generated list of user stories for the epic.
        """
        pass