"""
Unit tests for BacklogContainer.
"""

import pytest
from unittest.mock import AsyncMock

from backend.src.domain.exceptions.base.app_exception import AppException
from backend.src.infrastructure.di.WorkflowContainer import WorkflowContainer


def test_workflow_container_initializes_agents_and_tools() -> None:
    """
    Container initializes all agents and tools.
    """
    container = WorkflowContainer()

    assert container.prompt_loader is not None
    assert container.product_context_builder_agent is not None
    assert container.market_query_generator_agent is not None
    assert container.web_search_agent is not None
    assert container.backlog_generation_orchestrator_agent is not None

    assert container.product_context_tool is not None
    assert container.market_query_tool is not None
    assert container.web_search_tool is not None
    assert container.market_summary_tool is not None
    assert container.market_validation_tool is not None
    assert container.backlog_generation_tool is not None
    assert container.user_backlog_fixer_tool is not None
    assert container.delivery_planning_tool is not None


@pytest.mark.asyncio
async def test_initialize_workflow_workflow_orchestrator_sets_use_case(monkeypatch) -> None:
    """
    Initialization builds orchestrator and use case.
    """
    container = WorkflowContainer()

    orchestrator = AsyncMock()
    monkeypatch.setattr(
        "backend.src.infrastructure.di.workflow_container.BacklogWorkflowOrchestrator.create",
        AsyncMock(return_value=orchestrator),
    )

    await container.initialize_backlog_workflow_orchestrator()

    assert container.backlog_workflow_orchestrator is orchestrator
    assert container.generate_backlog_use_case is not None


@pytest.mark.asyncio
async def test_initialize_web_search_tool_calls_agent_create() -> None:
    """
    Initialization triggers web search agent create.
    """
    container = WorkflowContainer()

    container.web_search_agent.create = AsyncMock()

    await container.initialize_web_search_tool()

    container.web_search_agent.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_backlog_workflow_orchestrator_factory_uses_create(monkeypatch) -> None:
    """
    Factory returns orchestrator from create().
    """
    container = WorkflowContainer()

    orchestrator = AsyncMock()
    monkeypatch.setattr(
        "backend.src.infrastructure.di.backlog_container.BacklogWorkflowOrchestrator.create",
        AsyncMock(return_value=orchestrator),
    )

    result = await container.backlog_workflow_orchestrator_factory()

    assert result is orchestrator


def test_backlog_container_init_wraps_error(monkeypatch) -> None:
    """
    Initialization wraps unexpected errors into AppException.
    """
    def _boom(self):
        raise RuntimeError("fail")

    monkeypatch.setattr(WorkflowContainer, "_init_backlog_agents", _boom)

    with pytest.raises(AppException):
        WorkflowContainer()
