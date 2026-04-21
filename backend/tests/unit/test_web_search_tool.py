"""
Unit tests for WebSearchTool.
"""

from unittest.mock import AsyncMock

import pytest

from backend.src.domain.exceptions.tool.tool_execution_exception import ToolExecutionException
from backend.src.infrastructure.external.backlog_generation.tools.web_search_tool import WebSearchTool


@pytest.mark.asyncio
async def test_web_search_tool_success() -> None:
    """
    Tool returns aggregated search results.
    """
    web_search = AsyncMock()
    web_search.ask_many.return_value = "result"

    tool = WebSearchTool(web_search)
    result = await tool(["q1", "q2"])

    assert result == "result"
    web_search.ask_many.assert_awaited_once_with(["q1", "q2"])


@pytest.mark.asyncio
async def test_web_search_tool_wraps_error() -> None:
    """
    Tool wraps unexpected errors into ToolExecutionException.
    """
    web_search = AsyncMock()
    web_search.ask_many.side_effect = RuntimeError("fail")

    tool = WebSearchTool(web_search)

    with pytest.raises(ToolExecutionException):
        await tool(["q1"])
