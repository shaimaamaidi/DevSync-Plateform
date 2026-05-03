"""
Domain DTO for task verification response.

This module defines the response structure returned by the task verification process.
It represents the result of comparing generated tasks with existing ClickUp tasks,
and determines whether each task should be created or updated.

Main class:
    VerifyTasksResponse
"""

from typing import List
from pydantic import BaseModel, Field

from backend.src.domain.entities.clickup.verified_task import VerifiedTask


class VerifyTasksResponse(BaseModel):
    """
    Representation of the result of task verification against ClickUp.

    This DTO encapsulates the outcome of the verification process where generated tasks
    are compared against existing ClickUp tasks to determine the required action
    (create or update).

    Attributes:
        total: Total number of verified tasks after processing.
        tasks: List of verified tasks with their computed actions (create/update).
    """

    total: int = Field(
        ...,
        description="Total number of tasks processed during verification."
    )

    tasks: List[VerifiedTask] = Field(
        ...,
        description="List of verified tasks with their corresponding actions (create or update)."
    )