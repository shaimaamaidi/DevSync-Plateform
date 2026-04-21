"""
Service port for market query generation tool.

This module defines the IMarketQueryGeneratorTool interface, which specifies a callable contract
for generating search queries from a product description. These queries are intended to be used
for external market research and information retrieval.
"""

from abc import ABC, abstractmethod


class IMarketQueryGeneratorTool(ABC):
    """
    Define market query generation tool behavior required by the application.

    This interface represents a callable tool responsible for transforming a product or feature
    description into a set of search queries used for market analysis, competitor research, and
    external data enrichment.
    """

    @abstractmethod
    async def __call__(self, detailed_description: str) -> str:
        """
        Generate market search queries from a product description.

        Args:
            detailed_description (str): Raw product or feature description.

        Returns:
            str: Generated search queries as a structured or serialized text format.
        """
        pass