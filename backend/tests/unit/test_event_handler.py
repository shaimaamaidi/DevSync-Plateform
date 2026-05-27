"""
Unit tests for EventHandler.
"""

from types import SimpleNamespace

import pytest

from backend.src.infrastructure.external.backlog_generation.orchestrator.event_handler import EventHandler


def _message_delta(message_id: str, values: list[str]) -> SimpleNamespace:
    """
    Build a minimal message delta payload for the event handler.
    """
    content = [SimpleNamespace(text={"value": value}) for value in values]
    return SimpleNamespace(id=message_id, delta=SimpleNamespace(content=content))


@pytest.mark.asyncio
async def test_on_message_delta_accumulates_and_queues_chunks() -> None:
    """
    Test that message deltas are accumulated and emitted in FIFO order.
    """
    handler = EventHandler()

    await handler.on_message_delta(_message_delta("msg-1", ["Hello ", "world"]))
    await handler.on_message_delta(_message_delta("msg-1", ["!"]))

    assert handler.has_chunks() is True
    assert list(handler.get_stream_chunks()) == ["Hello world", "!"]
    assert handler.has_chunks() is False


@pytest.mark.asyncio
async def test_on_message_delta_resets_accumulation_for_new_message() -> None:
    """
    Test that a new message id resets the accumulated text state.
    """
    handler = EventHandler()

    await handler.on_message_delta(_message_delta("msg-1", ["First"]))
    await handler.on_message_delta(_message_delta("msg-2", ["Second"]))

    assert list(handler.get_stream_chunks()) == ["First", "Second"]


@pytest.mark.asyncio
async def test_on_thread_message_resets_state_on_completed_assistant_message() -> None:
    """
    Test that a completed assistant thread message clears the active message state.
    """
    handler = EventHandler()

    await handler.on_message_delta(_message_delta("msg-1", ["Chunk"]))
    await handler.on_thread_message(SimpleNamespace(status="completed", role="assistant"))

    assert handler.has_chunks() is True
    assert list(handler.get_stream_chunks()) == ["Chunk"]


@pytest.mark.asyncio
async def test_noop_event_callbacks_do_not_raise() -> None:
    """
    Test that the no-op event callbacks complete without raising.
    """
    handler = EventHandler()

    await handler.on_thread_run(SimpleNamespace(status="failed"))
    await handler.on_run_step(SimpleNamespace(status="completed", type="tool_calls", step_details=SimpleNamespace(tool_calls=[])))
    await handler.on_run_step_delta(SimpleNamespace(delta=SimpleNamespace(step_details=SimpleNamespace(tool_calls=[]))))
    await handler.on_unhandled_event("custom", {"x": 1})
    await handler.on_error("boom")
    await handler.on_done()
