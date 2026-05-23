"""
Domain DTO for task verification request (summary-based tasks).

This module defines the input structure used to verify generated tasks
against existing ClickUp tasks.

The request provides the necessary context (ClickUp space + generated tasks)
to allow the system to determine whether each task should be created or updated
based on comparison with existing ClickUp data.

Main class:
    VerifiedTaskFromSummaryRequest
"""

from typing import List
from pydantic import BaseModel, Field

from backend.src.domain.entities.generated_tasks.generated_task_from_summary import GeneratedTaskFromSummary


class VerifiedTaskFromSummaryRequest(BaseModel):
    """
    Representation of a task verification request from summary-based generation.

    This DTO is used to submit a batch of generated tasks to the verification
    workflow. Each task is compared against existing ClickUp tasks to determine
    whether it should be created or updated.

    Attributes:
        space_id: Identifier of the ClickUp workspace where tasks will be verified.
        tasks: List of generated tasks to validate against existing ClickUp tasks.
    """
    space_id: str = Field(..., min_length=1, description="Identifier of the ClickUp workspace.")
    tasks: List[GeneratedTaskFromSummary] = Field(..., description="List of generated tasks from summary to verify against ClickUp.")