"""
Service port for backlog generation tool.

This module defines the IBacklogGeneratorTool interface, which specifies a callable contract
for generating a backlog from a product description and contextual information. It is designed
to be used as a tool-like abstraction in the generation pipeline.
"""

from abc import ABC, abstractmethod


class IBacklogGeneratorTool(ABC):
    """
    Define backlog generation tool behavior required by the application.

    This interface represents a callable tool responsible for generating a structured backlog
    from a detailed product description and additional contextual information such as market
    intelligence or analysis results.
    """

    @abstractmethod
    async def __call__(self, detailed_description: str, context: str) -> str:
        """
        Generate a backlog from a product description and context.

        Args:
            detailed_description (str): Detailed product or feature description.
            context (str): Additional contextual information (e.g., market intelligence).

        Returns:
            str: Generated backlog as a structured text or serialized format.
        """
        pass