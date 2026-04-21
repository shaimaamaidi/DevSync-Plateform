"""
Service port for product context building.

This module defines the IProductContextBuilder interface, which specifies operations
for transforming a raw user description into a structured product context used
throughout the backlog generation workflow.
"""

from abc import ABC, abstractmethod

from backend.src.domain.entities.product.initial_description import InitialDescription


class IProductContextBuilder(ABC):
    """
    Define product context building behavior required by the application.

    This interface is responsible for converting a raw textual product description into a
    structured InitialDescription object that captures product overview, features, users,
    goals, and constraints.
    """

    @abstractmethod
    def build_context(self, description: str) -> InitialDescription:
        """
        Build a structured product context from a raw description.

        Args:
            description (str): Raw product or feature description provided by the user.

        Returns:
            InitialDescription: Structured representation of the product context.
        """
        pass