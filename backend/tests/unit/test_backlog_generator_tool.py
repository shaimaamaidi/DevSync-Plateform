"""
Unit tests for BacklogGeneratorTool.
"""

import json
from unittest.mock import AsyncMock

import pytest

from backend.src.domain.entities.backlog.backlog_structure import BacklogStructure, EpicBacklog, UserStoryWithTasks
from backend.src.domain.entities.backlog.epic import Epic
from backend.src.domain.entities.backlog.task import Task
from backend.src.domain.entities.backlog.user_story import UserStory
from backend.src.domain.entities.market.refined_market_intelligence import RefinedMarketIntelligenceSummary
from backend.src.domain.entities.product.initial_description import InitialDescription
from backend.src.domain.exceptions.tool.invalid_tool_argument_exception import InvalidToolArgumentException
from backend.src.domain.exceptions.tool.tool_execution_exception import ToolExecutionException
from backend.src.infrastructure.external.backlog_generation.tools.backlog_generator_tool import BacklogGeneratorTool


def _valid_description_json() -> str:
    return InitialDescription(
        product_overview="CRM for SMBs",
        target_users=["sales", "support"],
        core_features=["pipeline", "contacts"],
        business_goals=["increase retention"],
        constraints=["gdpr"],
        summary="A CRM to track deals and customers.",
    ).model_dump_json()


def _valid_context_json() -> str:
    return RefinedMarketIntelligenceSummary(
        refined_market_trends="CRMs are moving to AI assistance.",
        refined_competitor_features=["email sync"],
        refined_user_pain_points=["manual data entry"],
        refined_best_practices=["simple onboarding"],
        refined_enrichment_notes="Focus on quick setup.",
        cause="",
        is_valid=True,
    ).model_dump_json()


def _backlog_structure() -> BacklogStructure:
    return BacklogStructure(
        epics=[
            EpicBacklog(
                epic=Epic(title="Sales", description="Sales workflows"),
                user_stories=[
                    UserStoryWithTasks(
                        user_story=UserStory(title="Track leads", description="As a user..."),
                        tasks=[Task(title="Create lead", description="Implement create")],
                    )
                ],
            )
        ]
    )


@pytest.mark.asyncio
async def test_backlog_generator_tool_success() -> None:
    """
    Tool returns generated backlog JSON when inputs are valid.
    """
    orchestrator = AsyncMock()
    orchestrator.generate.return_value = _backlog_structure()

    tool = BacklogGeneratorTool(orchestrator)
    result = await tool(_valid_description_json(), _valid_context_json())

    parsed = json.loads(result)
    assert parsed["epics"][0]["epic"]["title"] == "Sales"
    orchestrator.generate.assert_awaited_once()


@pytest.mark.asyncio
async def test_backlog_generator_tool_invalid_description() -> None:
    """
    Tool raises InvalidToolArgumentException on invalid description JSON.
    """
    orchestrator = AsyncMock()
    tool = BacklogGeneratorTool(orchestrator)

    with pytest.raises(InvalidToolArgumentException):
        await tool("not-json", _valid_context_json())


@pytest.mark.asyncio
async def test_backlog_generator_tool_invalid_context() -> None:
    """
    Tool raises InvalidToolArgumentException on invalid context JSON.
    """
    orchestrator = AsyncMock()
    tool = BacklogGeneratorTool(orchestrator)

    with pytest.raises(InvalidToolArgumentException):
        await tool(_valid_description_json(), "not-json")


@pytest.mark.asyncio
async def test_backlog_generator_tool_wraps_runtime_error() -> None:
    """
    Tool wraps unexpected errors into ToolExecutionException.
    """
    orchestrator = AsyncMock()
    orchestrator.generate.side_effect = RuntimeError("fail")

    tool = BacklogGeneratorTool(orchestrator)

    with pytest.raises(ToolExecutionException):
        await tool(_valid_description_json(), _valid_context_json())
