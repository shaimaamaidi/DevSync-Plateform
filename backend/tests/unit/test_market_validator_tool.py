"""
Unit tests for MarketValidatorTool.
"""

import json
from unittest.mock import MagicMock

import pytest

from backend.src.domain.entities.market.market_intelligence import MarketIntelligenceSummary
from backend.src.domain.entities.market.refined_market_intelligence import RefinedMarketIntelligenceSummary
from backend.src.domain.entities.product.initial_description import InitialDescription
from backend.src.domain.exceptions.tool.invalid_tool_argument_exception import InvalidToolArgumentException
from backend.src.domain.exceptions.tool.tool_execution_exception import ToolExecutionException
from backend.src.infrastructure.external.backlog_generation.tools.market_validator_tool import (
    MarketValidatorTool,
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


def _context_json() -> str:
    return MarketIntelligenceSummary(
        market_trends="AI CRMs are growing.",
        competitor_features=["automation"],
        user_pain_points=["manual entry"],
        best_practices=["simple onboarding"],
        enrichment_notes="Focus on speed.",
    ).model_dump_json()


def _refined() -> RefinedMarketIntelligenceSummary:
    return RefinedMarketIntelligenceSummary(
        refined_market_trends="AI CRMs are growing.",
        refined_competitor_features=["automation"],
        refined_user_pain_points=["manual entry"],
        refined_best_practices=["simple onboarding"],
        refined_enrichment_notes="Focus on speed.",
        cause="",
        is_valid=True,
    )


@pytest.mark.asyncio
async def test_market_validator_tool_success() -> None:
    """
    Tool validates and returns refined context JSON.
    """
    validator = MagicMock()
    validator.validate_context.return_value = _refined()

    tool = MarketValidatorTool(validator)
    result = await tool(_description_json(), _context_json())

    parsed = json.loads(result)
    assert parsed["is_valid"] is True
    validator.validate_context.assert_called_once()


@pytest.mark.asyncio
async def test_market_validator_tool_invalid_description() -> None:
    """
    Tool raises InvalidToolArgumentException on invalid description JSON.
    """
    tool = MarketValidatorTool(MagicMock())

    with pytest.raises(InvalidToolArgumentException):
        await tool("not-json", _context_json())


@pytest.mark.asyncio
async def test_market_validator_tool_invalid_context() -> None:
    """
    Tool raises InvalidToolArgumentException on invalid context JSON.
    """
    tool = MarketValidatorTool(MagicMock())

    with pytest.raises(InvalidToolArgumentException):
        await tool(_description_json(), "not-json")


@pytest.mark.asyncio
async def test_market_validator_tool_wraps_error() -> None:
    """
    Tool wraps unexpected errors into ToolExecutionException.
    """
    validator = MagicMock()
    validator.validate_context.side_effect = RuntimeError("fail")

    tool = MarketValidatorTool(validator)

    with pytest.raises(ToolExecutionException):
        await tool(_description_json(), _context_json())
