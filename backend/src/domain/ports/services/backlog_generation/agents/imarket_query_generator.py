"""
Service port for market query generation.

This module defines the IMarketQueryGenerator interface, which specifies operations
for generating search queries from a structured product description in order to
retrieve relevant market and competitive information.
"""

from abc import ABC, abstractmethod

from backend.src.domain.entities.market.query import QueryGeneration
from backend.src.domain.entities.product.initial_description import InitialDescription


class IMarketQueryGenerator(ABC):
    """
    Define market query generation behavior required by the application.

    This interface is responsible for transforming a structured product description
    into a set of search queries used for market research and external information retrieval.
    """

    @abstractmethod
    def generate_queries(
        self,
        detailed_description: InitialDescription,
    ) -> QueryGeneration:
        """
        Generate search queries from a product description.

        Args:
            detailed_description (InitialDescription): Structured product description.

        Returns:
            QueryGeneration: Generated list of search queries.
        """
        pass