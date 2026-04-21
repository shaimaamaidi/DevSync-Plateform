"""
Unit tests for MarketQueryGeneratorTool.
"""

import json
from unittest.mock import MagicMock

import pytest

from backend.src.domain.entities.market.query import QueryGeneration
from backend.src.domain.entities.product.initial_description import InitialDescription
from backend.src.domain.exceptions.tool.invalid_tool_argument_exception import InvalidToolArgumentException
from backend.src.domain.exceptions.tool.tool_execution_exception import ToolExecutionException
from backend.src.infrastructure.external.backlog_generation.tools.market_query_generator_tool import (
    MarketQueryGeneratorTool,
)


def _description_json() -> str:
    return InitialDescription(
        product_overview="CRM for SMBs",
        target_users=["sales"],
        core_features=["pipeline"],
        business_goals=["increase retention"],
        constraints=["gdpr"],
        summary="A CRM for small teams.",
    ).model_dump_json()


@pytest.mark.asyncio
async def test_market_query_generator_tool_success() -> None:
    """
    Tool returns generated queries as JSON.
    """
    generator = MagicMock()
    generator.generate_queries.return_value = QueryGeneration(queries=["crm trends", "sales pipeline tools"])

    tool = MarketQueryGeneratorTool(generator)
    result = await tool(_description_json())

    parsed = json.loads(result)
    assert parsed["queries"][0] == "crm trends"
    generator.generate_queries.assert_called_once()


@pytest.mark.asyncio
async def test_market_query_generator_tool_invalid_description() -> None:
    """
    Tool raises InvalidToolArgumentException on invalid JSON.
    """
    tool = MarketQueryGeneratorTool(MagicMock())

    with pytest.raises(InvalidToolArgumentException):
        await tool("not-json")


@pytest.mark.asyncio
async def test_market_query_generator_tool_wraps_error() -> None:
    """
    Tool wraps unexpected errors into ToolExecutionException.
    """
    generator = MagicMock()
    generator.generate_queries.side_effect = RuntimeError("fail")

    tool = MarketQueryGeneratorTool(generator)

    with pytest.raises(ToolExecutionException):
        await tool(_description_json())
