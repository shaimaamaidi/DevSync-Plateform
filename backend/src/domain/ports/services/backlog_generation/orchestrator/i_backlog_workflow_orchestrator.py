"""
Service port for backlog workflow orchestration.

This module defines the IBacklogWorkflowOrchestrator interface, which specifies operations
for managing the full backlog generation workflow in a streaming manner, including initial
generation and iterative user feedback refinement.
"""

from abc import ABC, abstractmethod
from typing import AsyncGenerator, Optional


class IBacklogWorkflowOrchestrator(ABC):
    """
    Define backlog workflow orchestration behavior required by the application.

    This interface is responsible for coordinating the end-to-end backlog generation process,
    including:
        - Initial backlog generation from a description (streaming)
        - Iterative refinement based on market intelligence feedback
        - Iterative refinement based on user backlog modifications

    All operations are designed to be streaming to support progressive response generation.
    """

    @abstractmethod
    async def start_stream(self, description: str, thread_id: Optional[str] = None) -> AsyncGenerator[str, None]:
        """
        Start the backlog generation workflow as a stream.

        Args:
            description (str): Raw product or feature description.
            thread_id: Identifier of the conversation thread.
        Returns:
            AsyncGenerator[str, None]: Stream of generated backlog chunks.
        """
        yield ""

    @abstractmethod
    async def reply_stream(
        self,
        thread_id: str,
        tool_result: str,
        user_result: str,
    ) -> AsyncGenerator[str, None]:
        """
        Continue workflow based on market intelligence feedback.

        Args:
            thread_id (str): Conversation or workflow thread identifier.
            tool_result (str): Previous system-generated result to refine.
            user_result (str): User feedback or validation input.

        Returns:
            AsyncGenerator[str, None]: Stream of updated results.
        """
        yield ""

    @abstractmethod
    async def reply_backlog_stream(
        self,
        thread_id: str,
        user_result: str,
        tool_result: str,
    ) -> AsyncGenerator[str, None]:
        """
        Continue workflow based on user backlog modifications.

        Args:
            thread_id (str): Conversation or workflow thread identifier.
            user_result (str): User modifications or corrections to backlog.
            tool_result (str): Previous system-generated backlog.

        Returns:
            AsyncGenerator[str, None]: Stream of updated backlog results.
        """
        yield ""

    @abstractmethod
    async def generate_delivery_plan_stream(
            self,
            thread_id: str,
            backlog: str
    ) -> AsyncGenerator[str, None]:
        """
        Trigger delivery planning directly from a confirmed backlog.

        Called when the user confirms the backlog without modifications,
        skipping fix_user_backlog and proceeding straight to delivery_planning.

        Args:
            thread_id (str): Active Azure agent thread identifier.
            backlog (str): Confirmed backlog JSON string.

        Yields:
            AsyncGenerator[str, None]: Streaming chunks of delivery planning output.
        """
        yield ""