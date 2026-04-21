"""
Service port for market summarization tool.

This module defines the IMarketSummarizerTool interface, which specifies a callable contract
for generating a structured market intelligence summary from a product description and optional
web search results. It is used to enrich product context with external knowledge.
"""

from abc import ABC, abstractmethod
from typing import Optional


class IMarketSummarizerTool(ABC):
    """
    Define market summarization tool behavior required by the application.

    This interface represents a callable tool responsible for transforming a product description
    and optional web results into a structured market intelligence summary used for backlog
    generation and refinement.
    """

    @abstractmethod
    async def __call__(self, detailed_description: str, web_result: Optional[str] = None) -> str:
        """
        Generate a market intelligence summary from product description and web data.

        Args:
            detailed_description (str): Raw product or feature description.
            web_result (Optional[str]): Optional raw web search results used for enrichment.

        Returns:
            str: Market intelligence summary as structured or serialized text.
        """
        pass