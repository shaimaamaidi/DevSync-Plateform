"""
Domain DTO for starting backlog generation request.

This module defines the StartBacklogRequest DTO used to initiate the backlog generation workflow.
It contains the initial user-provided description that will be transformed into a structured backlog
through the generation pipeline.

Main classes:
    StartBacklogRequest
"""
from typing import Optional

from pydantic import BaseModel, Field


class StartBacklogRequest(BaseModel):
    """
    Request payload to start backlog generation.

    This DTO represents the initial input provided by the user to start the backlog creation process.
    The description is used as the source input for generating epics, user stories, and tasks.

    Attributes:
        thread_id: Identifier of the conversation thread.
        description: Raw functional or product description used to generate the backlog.
    """
    thread_id: Optional[str] = Field(default=None, description="Conversation thread identifier.")
    description: str = Field(..., min_length=1, description="Functional or product description used for backlog generation.")