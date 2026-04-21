"""
Azure AI Agents streaming event handler.

This module defines an event handler for processing streaming responses
from Azure AI Agents. It captures message deltas, tool executions, run
states, and errors in real-time while accumulating streamed output for
downstream consumption.

The handler is designed for:
- Streaming response aggregation
- Tool call monitoring
- Debugging and observability
- Incremental LLM output processing in agent workflows
"""

from typing import Generator
from azure.ai.agents.models import (
    RunStepDeltaChunk,
    RunStep,
    ThreadRun,
    ThreadMessage,
    MessageDeltaChunk,
    AsyncAgentEventHandler,
)


class EventHandler(AsyncAgentEventHandler):
    """
    Event handler for Azure AI Agents streaming execution.

    This handler is responsible for:
    - Capturing incremental assistant message deltas
    - Tracking tool calls and execution steps
    - Accumulating streamed text responses
    - Exposing collected chunks for external streaming pipelines

    Attributes:
        _current_message_id (str | None): Identifier of the currently processed message.
        _accumulated_text (str): Full aggregated assistant response during streaming.
        _stream_queue (list[str]): Queue of incremental text chunks ready for consumption.
    """

    def __init__(self):
        """
        Initialize the streaming event handler.
        """
        super().__init__()
        self._current_message_id = None
        self._accumulated_text = ""
        self._stream_queue = []

    async def on_message_delta(self, delta: MessageDeltaChunk) -> None:
        """
        Handle incremental message updates from the assistant.

        Args:
            delta (MessageDeltaChunk): Partial message content streamed from the model.
        """
        if delta.id != self._current_message_id:
            self._current_message_id = delta.id
            self._accumulated_text = ""

        partial_text = ""
        if delta.delta.content:
            for chunk in delta.delta.content:
                partial_text += chunk.text.get("value", "")

        self._accumulated_text += partial_text

        if partial_text:
            self._stream_queue.append(partial_text)

    async def on_thread_message(self, message: ThreadMessage) -> None:
        """
        Handle completed or status updates for thread messages.

        Args:
            message (ThreadMessage): Full message object from the thread.
        """
        if message.status == "completed" and message.role == "assistant":
            self._current_message_id = None
            self._accumulated_text = ""

    async def on_thread_run(self, run: ThreadRun) -> None:
        """
        Handle execution status updates for a thread run.

        Args:
            run (ThreadRun): Current execution run state.
        """
        if run.status == "failed":
            pass

    async def on_run_step(self, step: RunStep) -> None:
        """
        Handle execution steps including tool calls.

        Args:
            step (RunStep): A single execution step in the agent run.
        """
        if step.status == "completed" and str(step.type) == "tool_calls":
            if step.step_details and step.step_details.tool_calls:
                for tool_call in step.step_details.tool_calls:
                    if getattr(tool_call, "function", None):
                        pass

    async def on_run_step_delta(self, delta: RunStepDeltaChunk) -> None:
        """
        Handle incremental updates for run steps (e.g., tool call streaming).

        Args:
            delta (RunStepDeltaChunk): Partial execution step update.
        """
        if delta.delta.step_details and delta.delta.step_details.tool_calls:
            for tcall in delta.delta.step_details.tool_calls:
                if getattr(tcall, "function", None) and tcall.function.name:
                    pass

    async def on_unhandled_event(self, event_type: str, event_data) -> None:
        """
        Handle unknown or unhandled event types.

        Args:
            event_type (str): Name of the unhandled event.

            event_data: Raw event payload.
        """
        pass

    async def on_error(self, data: str) -> None:
        """
        Handle runtime or streaming errors.

        Args:
            data (str): Error message or payload.
        """
        pass

    async def on_done(self) -> None:
        """
        Called when the streaming process is completed.
        """
        pass

    def get_stream_chunks(self) -> Generator[str, None, None]:
        """
        Retrieve accumulated streaming text chunks.

        Returns:
            Generator[str, None, None]: Yields stored text chunks in FIFO order.
        """
        while self._stream_queue:
            yield self._stream_queue.pop(0)

    def has_chunks(self) -> bool:
        """
        Check if there are pending streamed chunks.

        Returns:
            bool: True if there are unconsumed chunks, False otherwise.
        """
        return len(self._stream_queue) > 0