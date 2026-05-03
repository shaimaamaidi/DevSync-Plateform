"""
Web search tool.

This module provides a tool responsible for executing multiple web search
queries and returning aggregated results. It acts as a bridge between external
LLM/tooling systems and the underlying IWebSearch service.

The tool delegates query execution to the web search service and returns the
raw aggregated response.
"""

import logging

from backend.src.domain.exceptions.azure.azure_agent_runtime_exception import AzureAgentRuntimeException
from backend.src.domain.exceptions.tool.tool_execution_exception import ToolExecutionException
from backend.src.domain.ports.services.backlog_generation.agents.iweb_search import (
    IWebSearch,
)
from backend.src.domain.ports.services.backlog_generation.tools.iweb_search_tool import (
    IWebSearchTool,
)


logger = logging.getLogger(__name__)


class WebSearchTool(IWebSearchTool):
    """
    Tool responsible for performing multi-query web searches.

    This tool:
    - Receives a list of search questions
    - Delegates execution to IWebSearch.ask_many
    - Returns aggregated search results

    Attributes:
        web_search (IWebSearch): Service responsible for executing web search queries.
    """

    def __init__(self, web_search: IWebSearch) -> None:
        """
        Initialize the WebSearchTool.

        Args:
            web_search (IWebSearch): Service used to perform web search operations.
        """
        self.web_search = web_search

    async def __call__(self, questions: list[str]) -> str:
        """
        Execute multiple web search queries.

        Args:
            questions (list[str]): List of search queries to execute.

        Returns:
            str: Aggregated web search results.
        Raises:
            AzureAgentRuntimeException: If the underlying Azure agent runtime fails during execution.
            ToolExecutionException: If web search execution fails due to underlying IWebSearch service
                errors, network failures, or any unexpected runtime exception during query processing
                or result aggregation.
        """
        logger.info(
            "WebSearchTool called (queries_count=%s).",
            len(questions),
        )

        try:
            result = await self.web_search.ask_many(questions)

            logger.info("Web search completed successfully.")

            return result

        except AzureAgentRuntimeException:
            raise
        except Exception as e:
            logger.exception("WebSearchTool failed.")
            raise ToolExecutionException(
                message=f"Web search execution failed: {str(e)}."
            ) from e