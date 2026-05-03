"""
Service port for market intelligence summarization.

This module defines the IMarketIntelligenceSummarizer interface, which specifies operations
for generating structured market intelligence from a product description and optional web data.
"""

from abc import ABC, abstractmethod
from typing import Optional

from backend.src.domain.entities.market.intelligence import MarketIntelligenceSummary
from backend.src.domain.entities.product.initial_description import InitialDescription


class IMarketIntelligenceSummarizer(ABC):
    """
    Define market intelligence summarization behavior required by the application.

    This interface is responsible for transforming a structured product description and optional
    external web results into a consolidated market intelligence summary used to guide backlog
    generation and prioritization.
    """

    @abstractmethod
    def summarize_context(
        self,
        detailed_description: InitialDescription,
        web_result: Optional[str] = None,
    ) -> MarketIntelligenceSummary:
        """
        Generate a market intelligence summary from input context.

        Args:
            detailed_description (InitialDescription): Structured product description.
            web_result (Optional[str]): Optional raw web or search result content.

        Returns:
            MarketIntelligenceSummary: Structured market intelligence summary.
        """
        pass