"""
Service port for epic generation.

This module defines the IEpicGenerator interface, which specifies operations for generating
epics from a product description enriched with market intelligence.
"""

from abc import ABC, abstractmethod

from backend.src.domain.entities.backlog.epic import EpicList
from backend.src.domain.entities.market.refined_market_intelligence import RefinedMarketIntelligenceSummary
from backend.src.domain.entities.product.initial_description import InitialDescription


class IEpicGenerator(ABC):
    """
    Define epic generation behavior required by the application.

    This interface is responsible for generating high-level epics from a structured product
    description and refined market intelligence context. These epics serve as the first layer
    of the backlog hierarchy.
    """

    @abstractmethod
    def generate_epics(
        self,
        detailed_description: InitialDescription,
        context: RefinedMarketIntelligenceSummary,
    ) -> EpicList:
        """
        Generate a list of epics from product description and market intelligence.

        Args:
            detailed_description (InitialDescription): Structured product description.
            context (RefinedMarketIntelligenceSummary): Refined market intelligence context.

        Returns:
            EpicList: Generated list of epics.
        """
        pass