"""
Unit tests for WebSearchAgent.
"""

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from backend.src.domain.exceptions.azure.azure_agent_runtime_exception import AzureAgentRuntimeException
from backend.src.infrastructure.external.backlog_generation.agents.web_search_agent import WebSearchAgent
from backend.src.infrastructure.external.backlog_generation.common.base_azure_project_agent import (
    BaseAzureProjectAgent,
)


class _AsyncMessages:
    def __init__(self, messages):
        self._messages = list(messages)

    def __aiter__(self):
        return self

    async def __anext__(self):
        if not self._messages:
            raise StopAsyncIteration
        return self._messages.pop(0)


def _patch_base_init(monkeypatch, project_client):
    def _fake_init(self, _key):
        self.agent_id = "agent-1"
        self.project_client = project_client
        self.agent = object()

    monkeypatch.setattr(BaseAzureProjectAgent, "__init__", _fake_init)


def _make_project_client_with_message(text_value: str):
    run = SimpleNamespace(id="run-1", status="completed", last_error=None)
    messages = _AsyncMessages([
        SimpleNamespace(
            role="assistant",
            content=[SimpleNamespace(type="text", text=SimpleNamespace(value=text_value))],
        )
    ])

    agents = SimpleNamespace(
        threads=SimpleNamespace(
            create=AsyncMock(return_value=SimpleNamespace(id="t-1")),
            delete=AsyncMock(),
        ),
        messages=SimpleNamespace(
            create=AsyncMock(),
            list=AsyncMock(return_value=messages),
        ),
        runs=SimpleNamespace(
            create=AsyncMock(return_value=run),
            get=AsyncMock(return_value=run),
        ),
    )
    return SimpleNamespace(agents=agents)


def _make_project_client_with_run_status(status: str, text_value: str = "answer"):
    run = SimpleNamespace(id="run-1", status=status, last_error="boom")
    messages = _AsyncMessages([
        SimpleNamespace(
            role="assistant",
            content=[SimpleNamespace(type="text", text=SimpleNamespace(value=text_value))],
        )
    ])

    agents = SimpleNamespace(
        threads=SimpleNamespace(
            create=AsyncMock(return_value=SimpleNamespace(id="t-1")),
            delete=AsyncMock(),
        ),
        messages=SimpleNamespace(
            create=AsyncMock(),
            list=AsyncMock(return_value=messages),
        ),
        runs=SimpleNamespace(
            create=AsyncMock(return_value=run),
            get=AsyncMock(return_value=run),
        ),
    )
    return SimpleNamespace(agents=agents)


@pytest.mark.asyncio
async def test_ask_many_returns_results(monkeypatch) -> None:
    """
    ask_many aggregates results from _ask_one.
    """
    project_client = _make_project_client_with_message("answer")
    _patch_base_init(monkeypatch, project_client)
    monkeypatch.setenv("BING_CONNECTION_NAME", "bing")

    agent = WebSearchAgent()

    async def _ask_one(_question):
        return "ok"

    monkeypatch.setattr(agent, "_ask_one", _ask_one)

    result = await agent.ask_many(["q1", "q2"])

    assert "Query: q1" in result
    assert "Result: ok" in result


@pytest.mark.asyncio
async def test_ask_many_all_errors_raise(monkeypatch) -> None:
    """
    ask_many raises AzureAgentRuntimeException when all queries fail.
    """
    project_client = _make_project_client_with_message("answer")
    _patch_base_init(monkeypatch, project_client)
    monkeypatch.setenv("BING_CONNECTION_NAME", "bing")

    agent = WebSearchAgent()

    async def _ask_one(_question):
        raise RuntimeError("fail")

    monkeypatch.setattr(agent, "_ask_one", _ask_one)

    with pytest.raises(AzureAgentRuntimeException):
        await agent.ask_many(["q1", "q2"])


@pytest.mark.asyncio
async def test_ask_many_partial_errors_returns_result(monkeypatch) -> None:
    """
    ask_many returns partial results when some queries fail.
    """
    project_client = _make_project_client_with_message("answer")
    _patch_base_init(monkeypatch, project_client)
    monkeypatch.setenv("BING_CONNECTION_NAME", "bing")

    agent = WebSearchAgent()

    async def _ask_one(question):
        if question == "q1":
            return "ok"
        raise RuntimeError("fail")

    monkeypatch.setattr(agent, "_ask_one", _ask_one)

    result = await agent.ask_many(["q1", "q2"])

    assert "Query: q1" in result
    assert "Query: q2" in result
    assert "Error -" in result


@pytest.mark.asyncio
async def test_ask_one_empty_question_returns_empty(monkeypatch) -> None:
    """
    _ask_one returns empty string for empty question.
    """
    project_client = _make_project_client_with_message("answer")
    _patch_base_init(monkeypatch, project_client)
    monkeypatch.setenv("BING_CONNECTION_NAME", "bing")

    agent = WebSearchAgent()

    result = await agent._ask_one("")

    assert result == ""


@pytest.mark.asyncio
async def test_ask_one_returns_assistant_text(monkeypatch) -> None:
    """
    _ask_one returns assistant response text when run completes.
    """
    project_client = _make_project_client_with_message("answer")
    _patch_base_init(monkeypatch, project_client)
    monkeypatch.setenv("BING_CONNECTION_NAME", "bing")

    agent = WebSearchAgent()

    async def _run(coro_factory):
        return await coro_factory()

    agent._retry.run = _run

    result = await agent._ask_one("question")

    assert result == "answer"
    project_client.agents.messages.create.assert_awaited_once()
    project_client.agents.runs.create.assert_awaited_once()
    project_client.agents.threads.delete.assert_awaited_once()


@pytest.mark.asyncio
async def test_ask_one_run_failed_raises(monkeypatch) -> None:
    """
    _ask_one raises AzureAgentRuntimeException when run is not completed.
    """
    project_client = _make_project_client_with_run_status("failed")
    _patch_base_init(monkeypatch, project_client)
    monkeypatch.setenv("BING_CONNECTION_NAME", "bing")

    agent = WebSearchAgent()

    async def _run(coro_factory):
        return await coro_factory()

    agent._retry.run = _run

    with pytest.raises(AzureAgentRuntimeException):
        await agent._ask_one("question")

    project_client.agents.threads.delete.assert_awaited_once()


@pytest.mark.asyncio
async def test_ask_one_no_assistant_text_returns_fallback(monkeypatch) -> None:
    """
    _ask_one returns fallback when no assistant text is found.
    """
    run = SimpleNamespace(id="run-1", status="completed", last_error=None)
    messages = _AsyncMessages([
        SimpleNamespace(
            role="assistant",
            content=[SimpleNamespace(type="image", text=SimpleNamespace(value="x"))],
        )
    ])
    agents = SimpleNamespace(
        threads=SimpleNamespace(
            create=AsyncMock(return_value=SimpleNamespace(id="t-1")),
            delete=AsyncMock(),
        ),
        messages=SimpleNamespace(
            create=AsyncMock(),
            list=AsyncMock(return_value=messages),
        ),
        runs=SimpleNamespace(
            create=AsyncMock(return_value=run),
            get=AsyncMock(return_value=run),
        ),
    )
    project_client = SimpleNamespace(agents=agents)
    _patch_base_init(monkeypatch, project_client)
    monkeypatch.setenv("BING_CONNECTION_NAME", "bing")

    agent = WebSearchAgent()

    async def _run(coro_factory):
        return await coro_factory()

    agent._retry.run = _run

    result = await agent._ask_one("question")

    assert result == "No response found"


@pytest.mark.asyncio
async def test_ask_one_uses_retry_run(monkeypatch) -> None:
    """
    _ask_one delegates execution to retry.run.
    """
    project_client = _make_project_client_with_message("answer")
    _patch_base_init(monkeypatch, project_client)
    monkeypatch.setenv("BING_CONNECTION_NAME", "bing")

    agent = WebSearchAgent()

    async def _run(coro_factory):
        return await coro_factory()

    agent._retry.run = AsyncMock(side_effect=_run)

    result = await agent._ask_one("question")

    assert result == "answer"
    agent._retry.run.assert_awaited_once()
