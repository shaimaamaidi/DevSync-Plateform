"""
Service port for web search tool.

This module defines the IWebSearchTool interface, which specifies a callable contract
for executing multiple web search queries and retrieving aggregated external information.
It is used to enrich market intelligence and product context with real-world data.
"""

from abc import ABC, abstractmethod


class IWebSearchTool(ABC):
    """
    Define web search tool behavior required by the application.

    This interface represents a callable tool responsible for executing a list of search
    queries against an external web source and returning aggregated results used for
    market research and context enrichment.
    """

    @abstractmethod
    async def __call__(self, questions: list[str]) -> str:
        """
        Execute multiple web search queries.

        Args:
            questions (list[str]): List of search queries to execute.

        Returns:
            str: Aggregated web search results as structured or serialized text.
        """
        pass