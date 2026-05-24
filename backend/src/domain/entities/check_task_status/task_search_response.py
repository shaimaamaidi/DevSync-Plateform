"""
Domain DTO for task search responses.

This module defines the TaskSearchResponse DTO used to represent
the response of a task search operation.
It encapsulates a user-facing response message and the list
of matching ClickUp tasks returned from the search process.

Main classes:
    TaskSearchResponse
"""

from typing import List

from pydantic import BaseModel, Field

from backend.src.domain.entities.clickup.list_with_tasks import ClickUpTask


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
        response: User-facing message describing the search result.
        task: List of ClickUp tasks matching the search criteria.
    """
    response: str = Field(
        ...,
        description=(
            "User-facing message describing the search result, "
            "such as confirmation requests, task selection prompts, "
            "or no-result notifications."
        )
    )
    task: List[ClickUpTask] = Field(default_factory=list, description="List of ClickUp tasks matching the search criteria.")