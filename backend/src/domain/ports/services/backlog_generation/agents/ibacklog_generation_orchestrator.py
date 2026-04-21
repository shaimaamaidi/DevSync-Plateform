"""
Service port for backlog generation orchestration.

This module defines the IBacklogGenerationOrchestrator interface, which specifies the contract
for generating a structured backlog from a product description enriched with market intelligence.
"""

from abc import ABC, abstractmethod

from backend.src.domain.entities.backlog.backlog_structure import BacklogStructure
from backend.src.domain.entities.market.refined_market_intelligence import RefinedMarketIntelligenceSummary
from backend.src.domain.entities.product.initial_description import InitialDescription


class IBacklogGenerationOrchestrator(ABC):
    """
    Define backlog generation orchestration behavior required by the application.

    This interface is responsible for coordinating the process of transforming a detailed product
    description and refined market intelligence into a structured backlog composed of epics,
    user stories, and tasks.
    """

    @abstractmethod
    async def generate(
        self,
        detailed_description: InitialDescription,
        context: RefinedMarketIntelligenceSummary,
    ) -> BacklogStructure:
        """
        Generate a structured backlog from product description and market intelligence.

        Args:
            detailed_description (InitialDescription): Structured product description.
            context (RefinedMarketIntelligenceSummary): Refined market intelligence context.

        Returns:
            BacklogStructure: Generated backlog containing epics, user stories, and tasks.
        """
        pass