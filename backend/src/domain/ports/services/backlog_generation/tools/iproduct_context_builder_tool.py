"""
Service port for product context tool.

This module defines the IProductContextTool interface, which specifies a callable contract
for transforming a raw product description into a structured product context. This context
is used as a foundation for downstream market intelligence and backlog generation processes.
"""

from abc import ABC, abstractmethod


class IProductContextTool(ABC):
    """
    Define product context tool behavior required by the application.

    This interface represents a callable tool responsible for converting a raw textual product
    description into a structured representation that captures key product aspects such as
    overview, features, users, and constraints.
    """

    @abstractmethod
    async def __call__(self, description: str) -> str:
        """
        Build a structured product context from a raw description.

        Args:
            description (str): Raw product or feature description.

        Returns:
            str: Structured product context as serialized or formatted text.
        """
        pass