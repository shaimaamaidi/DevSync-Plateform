"""
Backlog generation API routes.

This module defines API endpoints for managing the backlog generation workflow
using a streaming-based interaction model with the AI orchestrator.

The API exposes endpoints to:
- Start a new backlog generation process
- Handle user feedback during market intelligence validation
- Handle user feedback during backlog validation

Routes:
    POST /start: Start a new backlog generation stream from a raw project description.
    POST /reply: Submit a user response during the market intelligence verification loop.
    POST /reply/backlog: Submit a user response during the backlog verification loop.
"""

import logging

from fastapi import APIRouter, Depends
from starlette.responses import StreamingResponse

from backend.src.application.use_cases.generate_backlog_use_case import GenerateBacklogUseCase
from backend.src.domain.entities.backlog.start_backlog_request import StartBacklogRequest
from backend.src.domain.entities.backlog.reply_stream_request import ReplyStreamRequest
from backend.src.domain.entities.backlog.reply_backlog_stream_request import ReplyBacklogStreamRequest
from backend.src.presentation.api.deps import get_backlog_use_case

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/start")
async def start(
    request: StartBacklogRequest,
    use_case: GenerateBacklogUseCase = Depends(get_backlog_use_case),
) -> StreamingResponse:
    """
    Start a new backlog generation workflow.

    This endpoint initializes the backlog generation process by:
    - Receiving a raw project description
    - Triggering the orchestrator workflow
    - Returning a streaming response (Server-Sent Events)

    Args:
        request (StartBacklogRequest):
            Request containing the raw project description.

        use_case (GenerateBacklogUseCase):
            Application use case responsible for orchestrating the workflow.

    Returns:
        StreamingResponse:
            A server-sent events (SSE) stream containing:
            - Thread initialization metadata
            - Incremental AI-generated outputs
    """
    logger.info("Starting backlog generation stream: description_length=%s.", len(request.description))

    return StreamingResponse(
        use_case.start(request),
        media_type="text/event-stream",
    )


@router.post("/reply")
async def reply(
    request: ReplyStreamRequest,
    use_case: GenerateBacklogUseCase = Depends(get_backlog_use_case),
) -> StreamingResponse:
    """
    Handle user response during market intelligence verification.

    This endpoint is used in the verification loop after the system generates
    market intelligence. It allows the user to:
    - Confirm the generated result
    - Submit a modified version

    The response is processed by the orchestrator to either:
    - Validate the result
    - Refine it further
    - Proceed to backlog generation if validated

    Args:
        request (ReplyStreamRequest):
            Contains:
            - thread_id: Active workflow thread identifier
            - tool_result: Previous tool-generated result
            - user_result: User-confirmed or modified result

        use_case (GenerateBacklogUseCase):
            Application use case handling the workflow continuation.

    Returns:
        StreamingResponse:
            SSE stream containing updated validation results or next workflow step.
    """
    logger.info("Replying to market intelligence verification: thread_id=%s.", request.thread_id)

    return StreamingResponse(
        use_case.reply(request),
        media_type="text/event-stream",
    )


@router.post("/reply/backlog")
async def reply_backlog(
    request: ReplyBacklogStreamRequest,
    use_case: GenerateBacklogUseCase = Depends(get_backlog_use_case),
) -> StreamingResponse:
    """
    Handle user response during backlog verification.

    This endpoint manages the backlog validation loop where the user:
    - Confirms the generated backlog
    - Or submits modifications

    The orchestrator will:
    - Validate and fix the backlog if needed
    - Ensure structural and logical consistency
    - Proceed to delivery planning once approved

    Args:
        request (ReplyBacklogStreamRequest):
            Contains:
            - thread_id: Active workflow thread identifier
            - tool_result: Original generated backlog
            - user_result: User-modified or confirmed backlog

        use_case (GenerateBacklogUseCase):
            Application use case handling backlog validation workflow.

    Returns:
        StreamingResponse:
            SSE stream containing:
            - Corrected backlog (if invalid)
            - Or transition to delivery planning
    """
    logger.info("Replying to backlog verification: thread_id=%s.", request.thread_id)

    return StreamingResponse(
        use_case.reply_backlog(request),
        media_type="text/event-stream",
    )