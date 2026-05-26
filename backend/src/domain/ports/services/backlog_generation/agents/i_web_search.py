"""
Service port for web search operations.

This module defines the IWebSearch interface, which specifies operations for executing
multiple search queries against an external web search provider and returning aggregated results.
"""

from abc import ABC, abstractmethod
from typing import List


class IWebSearch(ABC):
    """
    Define web search behavior required by the application.

    This interface is responsible for executing multiple search queries and retrieving
    relevant external information that can be used for market intelligence, analysis,
    or enrichment of product context.
    """

    @abstractmethod
    async def ask_many(self, questions: List[str]) -> str:
        """
        Execute multiple web search queries and return aggregated results.

        Args:
            questions (List[str]): List of search queries to execute.

        Returns:
            str: Aggregated search results as a raw or structured text response.
        """
        pass