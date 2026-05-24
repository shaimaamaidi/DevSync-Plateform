"""
Unit tests for WorkflowContainer.

These tests verify initialization, orchestrator creation, web search tool
initialization, factory behavior, cleanup, and error wrapping.
"""

import pytest
from unittest.mock import AsyncMock

from backend.src.domain.exceptions.base.app_exception import AppException
from backend.src.domain.exceptions.system.service_unavailable_exception import ServiceUnavailableException
from backend.src.infrastructure.di.clickup_container import WorkflowContainer


def test_workflow_container_initializes_agents_and_tools() -> None:
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
async def test_initialize_backlog_workflow_orchestrator_sets_use_case(monkeypatch) -> None:
    container = WorkflowContainer()

    orchestrator = AsyncMock()
    monkeypatch.setattr(
        "backend.src.infrastructure.di.WorkflowContainer.BacklogWorkflowOrchestrator.create",
        AsyncMock(return_value=orchestrator),
    )

    await container.initialize_backlog_workflow_orchestrator()

    assert container.backlog_workflow_orchestrator is orchestrator
    assert container.generate_backlog_use_case is not None


@pytest.mark.asyncio
async def test_initialize_web_search_tool_calls_agent_create() -> None:
    container = WorkflowContainer()

    container.web_search_agent.create = AsyncMock()

    await container.initialize_web_search_tool()

    container.web_search_agent.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_backlog_workflow_orchestrator_factory_uses_create(monkeypatch) -> None:
    container = WorkflowContainer()

    orchestrator = AsyncMock()
    monkeypatch.setattr(
        "backend.src.infrastructure.di.WorkflowContainer.BacklogWorkflowOrchestrator.create",
        AsyncMock(return_value=orchestrator),
    )

    result = await container.backlog_workflow_orchestrator_factory()

    assert result is orchestrator


def test_create_save_task_use_case_raises_when_clickup_missing() -> None:
    container = WorkflowContainer()
    # simulate missing clickup infra
    container.clickup_task_service = None
    container.clickup_writer = None

    with pytest.raises(ServiceUnavailableException):
        container.create_save_task_use_case(member_repo=object())


@pytest.mark.asyncio
async def test_cleanup_calls_agent_and_orchestrator_cleanup() -> None:
    container = WorkflowContainer()

    container.web_search_agent = AsyncMock()
    container.web_search_agent.cleanup = AsyncMock()

    container.backlog_workflow_orchestrator = AsyncMock()
    container.backlog_workflow_orchestrator.cleanup = AsyncMock()

    await container.cleanup()

    container.web_search_agent.cleanup.assert_awaited_once()
    container.backlog_workflow_orchestrator.cleanup.assert_awaited_once()


def test_workflow_container_init_wraps_error(monkeypatch) -> None:
    def _boom(self):
        raise RuntimeError("fail")

    monkeypatch.setattr(WorkflowContainer, "_init_backlog_agents", _boom)

    with pytest.raises(AppException):
        WorkflowContainer()
