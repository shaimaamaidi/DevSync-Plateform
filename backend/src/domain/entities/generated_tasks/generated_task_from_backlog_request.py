"""
Domain DTO for task generation from sprint backlog.

This module defines the input structure used to generate ClickUp tasks
from a sprint backlog using AI-based extraction.

The request represents a structured sprint backlog that will be transformed
into actionable tasks associated with a ClickUp workspace.

Main classes:
    GeneratedTaskFromBacklogRequest
"""

from pydantic import BaseModel, Field

from backend.src.domain.entities.sprint.sprint import Sprint


class GeneratedTaskFromBacklogRequest(BaseModel):
    """
    Representation of a task generation request from a sprint backlog.

    This DTO is used to transform sprint backlog data into structured
    ClickUp tasks through an AI-based generation pipeline.

    Attributes:
        sprint_backlog: Sprint backlog data used to generate tasks.
        space_id: Identifier of the ClickUp workspace where tasks will be created.
    """
    sprint_backlog: Sprint
    space_id: str = Field(..., min_length=1, description="Identifier of the ClickUp workspace.")