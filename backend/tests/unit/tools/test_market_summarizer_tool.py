"""
Unit tests for MarketSummarizerTool.
"""

import json
from unittest.mock import MagicMock

import pytest

from backend.src.domain.entities.market.intelligence import MarketIntelligenceSummary
from backend.src.domain.entities.product.initial_description import InitialDescription
from backend.src.domain.exceptions.tool.invalid_tool_argument_exception import InvalidToolArgumentException
from backend.src.domain.exceptions.tool.tool_execution_exception import ToolExecutionException
from backend.src.infrastructure.external.backlog_generation.tools.market_summarizer_tool import (
    MarketSummarizerTool,
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


def _summary() -> MarketIntelligenceSummary:
    return MarketIntelligenceSummary(
        market_trends="AI CRMs are growing.",
        competitor_features=["automation"],
        user_pain_points=["manual entry"],
        best_practices=["simple onboarding"],
        enrichment_notes="Focus on speed.",
    )


@pytest.mark.asyncio
async def test_market_summarizer_tool_success_without_web() -> None:
    """
    Tool returns summary when no web result is provided.
    """
    summarizer = MagicMock()
    summarizer.summarize_context.return_value = _summary()

    tool = MarketSummarizerTool(summarizer)
    result = await tool(_description_json())

    parsed = json.loads(result)
    assert parsed["market_trends"] == "AI CRMs are growing."
    summarizer.summarize_context.assert_called_once()


@pytest.mark.asyncio
async def test_market_summarizer_tool_success_with_web() -> None:
    """
    Tool passes web_result when provided.
    """
    summarizer = MagicMock()
    summarizer.summarize_context.return_value = _summary()

    tool = MarketSummarizerTool(summarizer)
    result = await tool(_description_json(), web_result="results")

    parsed = json.loads(result)
    assert parsed["market_trends"] == "AI CRMs are growing."
    summarizer.summarize_context.assert_called_once()


@pytest.mark.asyncio
async def test_market_summarizer_tool_invalid_description() -> None:
    """
    Tool raises InvalidToolArgumentException on invalid JSON.
    """
    tool = MarketSummarizerTool(MagicMock())

    with pytest.raises(InvalidToolArgumentException):
        await tool("not-json")


@pytest.mark.asyncio
async def test_market_summarizer_tool_wraps_error() -> None:
    """
    Tool wraps unexpected errors into ToolExecutionException.
    """
    summarizer = MagicMock()
    summarizer.summarize_context.side_effect = RuntimeError("fail")

    tool = MarketSummarizerTool(summarizer)

    with pytest.raises(ToolExecutionException):
        await tool(_description_json())
