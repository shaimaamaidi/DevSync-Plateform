"""
Service port for market intelligence validation.

This module defines the IMarketIntelligenceValidator interface, which specifies operations
for validating and refining market intelligence before it is used in backlog generation.
"""

from abc import ABC, abstractmethod

from backend.src.domain.entities.market.market_intelligence import MarketIntelligenceSummary
from backend.src.domain.entities.market.refined_market_intelligence import RefinedMarketIntelligenceSummary
from backend.src.domain.entities.product.initial_description import InitialDescription


class IMarketIntelligenceValidator(ABC):
    """
    Define market intelligence validation behavior required by the application.

    This interface is responsible for validating a generated market intelligence summary against
    the original product description and producing a refined version with corrections and validation status.
    """

    @abstractmethod
    def validate_context(
        self,
        detailed_description: InitialDescription,
        context: MarketIntelligenceSummary,
    ) -> RefinedMarketIntelligenceSummary:
        """
        Validate and refine a market intelligence context.

        Args:
            detailed_description (InitialDescription): Structured product description.
            context (MarketIntelligenceSummary): Generated market intelligence summary.

        Returns:
            RefinedMarketIntelligenceSummary: Validated and possibly corrected market intelligence.
        """
        pass