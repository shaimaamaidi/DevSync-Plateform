"""
Domain DTO for backlog streaming reply request.

This module defines the ReplyBacklogStreamRequest DTO used to handle user feedback
during backlog refinement in a streaming workflow. It carries the conversation thread
identifier along with both user-provided and tool-generated results to support iterative
backlog updates.

Main classes:
    ReplyBacklogStreamRequest
"""

from pydantic import BaseModel, Field


class ReplyBacklogStreamRequest(BaseModel):
    """
    Request payload for backlog refinement streaming.

    This DTO is used when a user provides feedback on a generated backlog.
    It allows the system to continue the backlog refinement workflow in a
    streaming manner using the existing conversation thread.

    Attributes:
        thread_id: Identifier of the conversation thread.
        user_result: User feedback or modifications on the backlog.
        tool_result: Previous system/tool generated backlog output.
    """
    thread_id: str = Field(..., min_length=1, description="Conversation thread identifier.")
    user_result: str = Field(..., description="User feedback or modifications on the backlog.")
    tool_result: str = Field(..., description="Previous system/tool generated backlog output.")