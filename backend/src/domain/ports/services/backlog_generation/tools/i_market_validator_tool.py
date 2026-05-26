"""
Service port for market validation tool.

This module defines the IMarketValidatorTool interface, which specifies a callable contract
for validating and refining market intelligence based on a product description and generated context.
It ensures consistency and correctness before downstream backlog generation.
"""

from abc import ABC, abstractmethod


class IMarketValidatorTool(ABC):
    """
    Define market validation tool behavior required by the application.

    This interface represents a callable tool responsible for validating and refining
    a market intelligence context against a product description to ensure accuracy,
    consistency, and usability in the backlog generation pipeline.
    """

    @abstractmethod
    async def __call__(self, detailed_description: str, context: str) -> str:
        """
        Validate and refine market intelligence context.

        Args:
            detailed_description (str): Raw product or feature description.
            context (str): Generated market intelligence context to validate.

        Returns:
            str: Validated and possibly refined market intelligence as structured text.
        """
        pass