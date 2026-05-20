"""
Domain DTO for streaming reply request.

This module defines the ReplyStreamRequest DTO used to handle user feedback
during the market intelligence or intermediate workflow validation phase.
It carries the conversation thread identifier along with tool-generated results
and user responses to support iterative refinement in a streaming process.

Main classes:
    ReplyStreamRequest
"""

from pydantic import BaseModel, Field


class ReplyStreamRequest(BaseModel):
    """
    Request payload for streaming workflow reply.

    This DTO is used when the user responds to a generated output (such as market intelligence)
    in order to validate, refine, or correct it within an ongoing conversation thread.

    Attributes:
        thread_id: Identifier of the conversation thread.
        tool_result: Output produced by the system or tool that is being reviewed.
        user_result: User feedback, corrections, or validation input.
    """
    thread_id: str = Field(...,min_length=1,description="Conversation thread identifier.")
    tool_result: str = Field(...,description="System or tool-generated output being reviewed.")
    user_result: str = Field(...,description="User feedback, corrections, or validation input.")