"""
Unit tests for BacklogWorkflowOrchestrator.
"""

import json
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from backend.src.domain.exceptions.stream.stream_execution_exception import StreamExecutionException
from backend.src.domain.exceptions.tool.invalid_tool_argument_exception import InvalidToolArgumentException
from backend.src.domain.exceptions.tool.tool_execution_exception import ToolExecutionException
from backend.src.infrastructure.external.backlog_generation.common.base_azure_project_agent import (
    BaseAzureProjectAgent,
)
from backend.src.infrastructure.external.backlog_generation.orchestrator.backlog_workflow_orchestrator import (
    BacklogWorkflowOrchestrator,
)


class _DummyStream:
    def __init__(self, events):
        self._events = list(events)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    def __aiter__(self):
        return self

    async def __anext__(self):
        if not self._events:
            raise StopAsyncIteration
        return self._events.pop(0)


class _EventHandlerStub:
    def __init__(self):
        self._chunks = []

    def get_stream_chunks(self):
        while self._chunks:
            yield self._chunks.pop(0)


def _patch_base_init(monkeypatch, project_client):
    def _fake_init(self, _key):
        self.agent_id = "agent-1"
        self.project_client = project_client
        self.agent = object()

    monkeypatch.setattr(BaseAzureProjectAgent, "__init__", _fake_init)


def _make_project_client(events):
    runs = SimpleNamespace(
        stream=AsyncMock(return_value=_DummyStream(events)),
        submit_tool_outputs_stream=AsyncMock(),
    )
    agents = SimpleNamespace(
        runs=runs,
        messages=SimpleNamespace(create=AsyncMock()),
        threads=SimpleNamespace(create=AsyncMock(return_value=SimpleNamespace(id="t-1"))),
    )
    return SimpleNamespace(agents=agents)


def _build_orchestrator(monkeypatch, project_client):
    _patch_base_init(monkeypatch, project_client)
    return BacklogWorkflowOrchestrator(
        product_context_tool=AsyncMock(),
        query_generator_tool=AsyncMock(),
        web_search_tool=AsyncMock(),
        market_summarizer_tool=AsyncMock(),
        market_validator_tool=AsyncMock(),
        backlog_generator_tool=AsyncMock(),
        user_backlog_fixer_tool=AsyncMock(),
        delivery_planner_tool=AsyncMock(),
    )


@pytest.mark.asyncio
async def test_start_stream_emits_thread_and_chunks(monkeypatch) -> None:
    """
    Start stream yields thread_id and downstream chunks.
    """
    project_client = _make_project_client(events=[])
    orchestrator = _build_orchestrator(monkeypatch, project_client)

    captured = {}

    async def _fake_run_stream(self, thread_id, tool_choice=None):
        captured["thread_id"] = thread_id
        captured["tool_choice"] = tool_choice
        yield "chunk"

    monkeypatch.setattr(BacklogWorkflowOrchestrator, "_run_stream", _fake_run_stream)

    results = [chunk async for chunk in orchestrator.start_stream("desc")]

    assert results[0] == "data: {\"thread_id\": \"t-1\"}\n\n"
    assert results[1] == "data: {\"text\": \"chunk\"}\n\n"
    assert captured["thread_id"] == "t-1"
    assert captured["tool_choice"]["function"]["name"] == "build_product_context"


@pytest.mark.asyncio
async def test_run_stream_submits_tool_outputs(monkeypatch) -> None:
    """
    Run stream submits tool outputs for tool calls.
    """
    tool_call = SimpleNamespace(
        id="call-1",
        function=SimpleNamespace(
            name="generate_backlog",
            arguments=json.dumps({"detailed_description": "{}", "context": "{}"}),
        ),
    )
    run_data = SimpleNamespace(
        id="run-1",
        required_action=SimpleNamespace(
            submit_tool_outputs=SimpleNamespace(tool_calls=[tool_call])
        ),
    )

    project_client = _make_project_client(
        events=[("thread.run.requires_action", run_data, None)]
    )
    orchestrator = _build_orchestrator(monkeypatch, project_client)

    orchestrator.backlog_generator_tool = AsyncMock(return_value={"ok": True})

    monkeypatch.setattr(
        "backend.src.infrastructure.external.backlog_generation.orchestrator.backlog_workflow_orchestrator.EventHandler",
        _EventHandlerStub,
    )

    results = [chunk async for chunk in orchestrator._run_stream("t-1")]

    assert results == []
    project_client.agents.runs.submit_tool_outputs_stream.assert_awaited_once()
    tool_outputs = project_client.agents.runs.submit_tool_outputs_stream.call_args.kwargs["tool_outputs"]
    payload = json.loads(tool_outputs[0]["output"])
    assert payload["success"] is True


@pytest.mark.asyncio
async def test_run_stream_invalid_json_arguments(monkeypatch) -> None:
    """
    Invalid JSON tool arguments produce invalid_json output.
    """
    tool_call = SimpleNamespace(
        id="call-1",
        function=SimpleNamespace(name="generate_backlog", arguments="{bad}"),
    )
    run_data = SimpleNamespace(
        id="run-1",
        required_action=SimpleNamespace(
            submit_tool_outputs=SimpleNamespace(tool_calls=[tool_call])
        ),
    )

    project_client = _make_project_client(
        events=[("thread.run.requires_action", run_data, None)]
    )
    orchestrator = _build_orchestrator(monkeypatch, project_client)

    monkeypatch.setattr(
        "backend.src.infrastructure.external.backlog_generation.orchestrator.backlog_workflow_orchestrator.EventHandler",
        _EventHandlerStub,
    )

    _ = [chunk async for chunk in orchestrator._run_stream("t-1")]

    tool_outputs = project_client.agents.runs.submit_tool_outputs_stream.call_args.kwargs["tool_outputs"]
    payload = json.loads(tool_outputs[0]["output"])
    assert payload["error_type"] == "invalid_json"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "exc,expected_type",
    [
        (InvalidToolArgumentException("bad"), "invalid_arguments"),
        (ToolExecutionException("fail"), "tool_execution"),
    ],
)
async def test_run_stream_tool_errors(monkeypatch, exc, expected_type) -> None:
    """
    Tool exceptions are captured and submitted with error types.
    """
    tool_call = SimpleNamespace(
        id="call-1",
        function=SimpleNamespace(
            name="generate_backlog",
            arguments=json.dumps({"detailed_description": "{}", "context": "{}"}),
        ),
    )
    run_data = SimpleNamespace(
        id="run-1",
        required_action=SimpleNamespace(
            submit_tool_outputs=SimpleNamespace(tool_calls=[tool_call])
        ),
    )

    project_client = _make_project_client(
        events=[("thread.run.requires_action", run_data, None)]
    )
    orchestrator = _build_orchestrator(monkeypatch, project_client)

    orchestrator.backlog_generator_tool = AsyncMock(side_effect=exc)

    monkeypatch.setattr(
        "backend.src.infrastructure.external.backlog_generation.orchestrator.backlog_workflow_orchestrator.EventHandler",
        _EventHandlerStub,
    )

    if expected_type == "tool_execution":
        with pytest.raises(StreamExecutionException):
            _ = [chunk async for chunk in orchestrator._run_stream("t-1")]
    else:
        _ = [chunk async for chunk in orchestrator._run_stream("t-1")]

        tool_outputs = project_client.agents.runs.submit_tool_outputs_stream.call_args.kwargs["tool_outputs"]
        payload = json.loads(tool_outputs[0]["output"])
        assert payload["error_type"] == expected_type

    @pytest.mark.asyncio
    async def test_reply_stream_posts_message_and_streams(monkeypatch) -> None:
        """
        Reply stream posts a message and delegates to _run_stream.
        """
        project_client = _make_project_client(events=[])
        orchestrator = _build_orchestrator(monkeypatch, project_client)

        async def _fake_run_stream(self, thread_id, tool_choice=None):
            yield "chunk"

        monkeypatch.setattr(BacklogWorkflowOrchestrator, "_run_stream", _fake_run_stream)

        results = [chunk async for chunk in orchestrator.reply_stream("t-1", "tool", "user")]

        assert results == ["data: {\"text\": \"chunk\"}\n\n"]
        project_client.agents.messages.create.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_reply_backlog_stream_posts_message_and_streams(monkeypatch) -> None:
        """
        Reply backlog stream posts a message and delegates to _run_stream.
        """
        project_client = _make_project_client(events=[])
        orchestrator = _build_orchestrator(monkeypatch, project_client)

        async def _fake_run_stream(self, thread_id, tool_choice=None):
            yield "fixed"

        monkeypatch.setattr(BacklogWorkflowOrchestrator, "_run_stream", _fake_run_stream)

        results = [chunk async for chunk in orchestrator.reply_backlog_stream("t-2", "user", "tool")]

        assert results == ["data: {\"text\": \"fixed\"}\n\n"]
        project_client.agents.messages.create.assert_awaited_once()
