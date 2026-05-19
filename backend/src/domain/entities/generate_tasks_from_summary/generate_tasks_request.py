"""
Domain DTO for task generation from meeting summary.

This module defines the input structure used to generate ClickUp tasks
from a meeting summary using AI-based extraction.

The request represents unstructured meeting notes that will be transformed
into structured tasks associated with a ClickUp workspace.

Main class:
    GenerateTasksFromSummaryRequest
"""

from pydantic import BaseModel, Field


class GenerateTasksFromSummaryRequest(BaseModel):
    """
    Representation of a task generation request from meeting notes.

    This DTO is used to transform a raw meeting summary into structured
    ClickUp tasks. The summary can be written in Arabic or French and is
    processed by an AI-based extraction pipeline.

    Attributes:
        meeting_summary: Raw meeting notes used to generate tasks (Arabic or French).
        space_id: Identifier of the ClickUp workspace where tasks will be created.
    """
    meeting_summary: str = Field(..., description="Raw meeting summary text used for task generation (Arabic).")
    space_id: str = Field(..., description="Identifier of the ClickUp workspace.")