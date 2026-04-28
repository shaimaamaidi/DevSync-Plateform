"""
Backlog generation use case module.

This module provides the GenerateBacklogUseCase class, which orchestrates the backlog generation workflow.
It acts as an application layer entry point for streaming backlog creation and refinement operations,
delegating the processing to the workflow orchestrator.

Classes:
    GenerateBacklogUseCase: Main use case for backlog generation and refinement (stream-based).
"""

import logging

from typing import AsyncGenerator

from backend.src.domain.entities.backlog.reply_backlog_stream_request import ReplyBacklogStreamRequest
from backend.src.domain.entities.backlog.reply_stream_request import ReplyStreamRequest
from backend.src.domain.entities.backlog.start_backlog_request import StartBacklogRequest
from backend.src.domain.exceptions.base.app_exception import AppException
from backend.src.domain.exceptions.backlog.backlog_reply_exception import BacklogReplyException
from backend.src.domain.exceptions.backlog.backlog_stream_exception import BacklogStreamException
from backend.src.domain.exceptions.stream.reply_stream_exception import ReplyStreamException
from backend.src.domain.ports.input.i_generate_backlog_use_case import IGenerateBacklogUseCase
from backend.src.domain.ports.services.backlog_generation.orchestrator.ibacklog_workflow_orchestrator import \
    IBacklogWorkflowOrchestrator


logger = logging.getLogger(__name__)


class GenerateBacklogUseCase(IGenerateBacklogUseCase):
    """
    Application use case for managing the backlog generation workflow.

    This class orchestrates the interaction between the presentation layer and the backlog workflow orchestrator.
    It handles:
        - Initial backlog generation stream
        - Market intelligence reply processing
        - Backlog refinement and correction stream

    All operations are streamed asynchronously to support progressive generation.

    Attributes:
        _orchestrator (IBacklogWorkflowOrchestrator): Workflow orchestrator handling business logic.
    """

    def __init__(self, orchestrator: IBacklogWorkflowOrchestrator) -> None:
        """
        Initialize the use case with a workflow orchestrator.

        Args:
            orchestrator (IBacklogWorkflowOrchestrator): Backlog workflow orchestrator implementation.
        """
        self._orchestrator = orchestrator

    async def start(self, request: StartBacklogRequest) -> AsyncGenerator[str, None]:
        """
        Start backlog generation from an initial user description.

        This method triggers the workflow that transforms a raw product or feature description
        into a structured backlog, streamed incrementally.

        Args:
            request (StartBacklogRequest): Request containing the initial backlog description.

        Returns:
            AsyncGenerator[str, None]: Stream of generated backlog chunks.

        Raises:
            AppException: If a known application-level error occurs during processing.
            BacklogStreamException: If an unexpected error occurs during backlog generation streaming.
        """
        logger.info(
            "Starting backlog generation stream: description_length=%s.",
            len(request.description)
        )

        try:
            async for chunk in self._orchestrator.start_stream(request.description):
                yield chunk
        except AppException:
            raise
        except Exception as e:
            logger.exception("Backlog generation stream failed: %s.", str(e))
            raise BacklogStreamException( f"Backlog generation failed: {str(e)}.") from e

        logger.info("Backlog generation stream completed successfully.")


    async def reply(self, request: ReplyStreamRequest) -> AsyncGenerator[str, None]:
        """
        Process user feedback for market intelligence validation.

        This method handles the iterative refinement loop where the user can validate or correct
        generated market intelligence before backlog generation continues.

        Args:
            request (ReplyStreamRequest): User reply containing validation or corrections.

        Returns:
            AsyncGenerator[str, None]: Stream of updated market intelligence response chunks.

        Raises:
            AppException: If a known application-level error occurs during processing.
            ReplyStreamException: If an unexpected error occurs during market intelligence reply streaming.
        """
        logger.info(
            "Replying to market intelligence verification: thread_id=%s.",
            request.thread_id
        )

        try:
            async for chunk in self._orchestrator.reply_stream(
                thread_id=request.thread_id,
                tool_result=request.tool_result,
                user_result=request.user_result,
            ):
                yield chunk
        except AppException:
            raise
        except Exception as e:
            logger.exception("Market intelligence reply failed: thread_id=%s, error=%s.", request.thread_id, str(e))
            raise ReplyStreamException( f"Market intelligence reply failed: {str(e)}.") from e

        logger.info(
            "Market intelligence reply processed successfully: thread_id=%s.",
            request.thread_id,
        )

    async def reply_backlog(self, request: ReplyBacklogStreamRequest) -> AsyncGenerator[str, None]:
        """
        Process user feedback for backlog refinement.

        This method allows the user to modify, correct, or enhance the generated backlog,
        including updates to epics, user stories, tasks, or estimations.

        Args:
            request (ReplyBacklogStreamRequest): User reply containing backlog modifications.

        Returns:
            AsyncGenerator[str, None]: Stream of updated backlog chunks.

        Raises:
            AppException: If a known application-level error occurs during processing.
            BacklogReplyException: If an unexpected error occurs during backlog refinement streaming.
        """
        logger.info(
            "Replying to backlog verification: thread_id=%s.",
            request.thread_id
        )

        try:
            async for chunk in self._orchestrator.reply_backlog_stream(
                thread_id=request.thread_id,
                user_result=request.user_result,
                tool_result=request.tool_result,
            ):
                yield chunk
        except AppException:
            raise
        except Exception as e:
            logger.exception("Backlog reply failed: thread_id=%s, error=%s.", request.thread_id, str(e))
            raise BacklogReplyException( f"Backlog reply failed: {str(e)}.") from e

        logger.info(
            "Backlog reply processed successfully: thread_id=%s.",
            request.thread_id,
        )