"""
Domain DTO for task search responses.

This module defines the TaskSearchResponse DTO used to represent
the result of a task search operation.

It encapsulates:
- The search status (no match, single match, multiple matches, etc.)
- A user-facing response message
- The list of ClickUp tasks matching the search criteria

Main classes:
    TaskSearchStatus, TaskSearchResponse
"""

from enum import Enum
from typing import List

from pydantic import BaseModel, Field

from backend.src.domain.entities.clickup.list_with_tasks import ClickUpTask


class TaskSearchStatus(str, Enum):
    """
    Enumeration of possible task search outcomes.

    Attributes:
        NO_TASKS_IN_SPACE: The selected ClickUp space contains no tasks.
        NO_MATCH: No tasks match the user's search query.
        SINGLE_MATCH: Exactly one task matches the search query.
        MULTIPLE_MATCHES: Multiple tasks match the search query.
    """
    NO_TASKS_IN_SPACE = "No_TASK_IN_SPACE"
    NO_MATCH = "NO_MATCH"
    SINGLE_MATCH = "SINGLE_MATCH"
    MULTIPLE_MATCHES = "MULTIPLES_MATCHES"

class TaskSearchResponse(BaseModel):
    """
    Representation of a task search response.

    This DTO contains the response message intended to be displayed
    to the user after a task search operation, along with the list
    of matching ClickUp tasks.

    The response message may:
    - Ask the user to confirm a task when a single match is found
    - Ask the user to choose a task when multiple matches are found
    - Inform the user that no matching tasks were found
    - Inform the user that the selected space does not contain tasks

    Attributes:
        status: Outcome of the search operation.
        message: User-facing message describing the search result.
        task: List of ClickUp tasks matching the search criteria.
    """
    status: TaskSearchStatus = Field(..., description="Outcome of the task search operation.")
    message: str = Field(
        ...,
        description=(
            "User-facing message describing the search result, "
            "such as confirmation requests, task selection prompts, "
            "or no-result notifications."
        )
    )
    task: List[ClickUpTask] = Field(default_factory=list, description="List of ClickUp tasks matching the search criteria.")