"""
Unit tests for ProductContextBuilderTool.
"""

import json
from unittest.mock import MagicMock

import pytest

from backend.src.domain.entities.product.initial_description import InitialDescription
from backend.src.domain.exceptions.tool.tool_execution_exception import ToolExecutionException
from backend.src.infrastructure.external.backlog_generation.tools.product_context_builder_tool import (
    ProductContextBuilderTool,
)


def _initial_description() -> InitialDescription:
    return InitialDescription(
        product_overview="CRM for SMBs",
        target_users=["sales"],
        core_features=["pipeline"],
        business_goals=["increase retention"],
        constraints=["gdpr"],
        summary="A CRM for small teams.",
    )


@pytest.mark.asyncio
async def test_product_context_builder_tool_success() -> None:
    """
    Tool returns JSON produced by builder.
    """
    builder = MagicMock()
    builder.build_context.return_value = _initial_description()

    tool = ProductContextBuilderTool(builder)
    result = await tool("raw description")

    parsed = json.loads(result)
    assert parsed["product_overview"] == "CRM for SMBs"
    builder.build_context.assert_called_once_with("raw description")


@pytest.mark.asyncio
async def test_product_context_builder_tool_wraps_error() -> None:
    """
    Tool wraps unexpected errors into ToolExecutionException.
    """
    builder = MagicMock()
    builder.build_context.side_effect = RuntimeError("fail")

    tool = ProductContextBuilderTool(builder)

    with pytest.raises(ToolExecutionException):
        await tool("raw description")
