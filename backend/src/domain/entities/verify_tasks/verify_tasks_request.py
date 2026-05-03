"""
Domain DTO for task verification request.

This module defines the input structure used to verify generated tasks
against existing ClickUp tasks.

The request provides the necessary context (ClickUp space + generated tasks)
to allow the system to determine whether each task should be created or updated.

Main class:
    VerifyTasksRequest
"""

from typing import List
from pydantic import BaseModel, Field

from backend.src.domain.entities.clickup.generated_task import GeneratedTask


class VerifyTasksRequest(BaseModel):
    """
    Representation of a task verification request.

    This DTO is used to submit a batch of generated tasks to the verification
    workflow. Each task is compared against existing ClickUp data to determine
    whether it should be created or updated.

    Attributes:
        space_id: Identifier of the ClickUp workspace where tasks will be verified.
        tasks: List of generated tasks to be validated against existing ClickUp tasks.
    """

    space_id: str = Field(
        ...,
        description="Identifier of the ClickUp workspace."
    )

    tasks: List[GeneratedTask] = Field(
        ...,
        description="List of generated tasks to verify against ClickUp."
    )