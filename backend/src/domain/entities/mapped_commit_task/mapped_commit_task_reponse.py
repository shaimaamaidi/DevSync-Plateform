"""
Domain DTO for commit-to-task mapping responses.

This module defines the MappedCommitTaskResponse DTO used to represent
the result of mapping a GitHub commit to a ClickUp task.

It encapsulates:
- The mapping status (found, not found, empty workspace)
- A user-facing message describing the result
- The matched ClickUp task if a match is found

Main classes:
    CommitTaskMappingStatus
    MappedCommitTaskResponse
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from backend.src.domain.entities.clickup.list_with_tasks import ClickUpTask


class CommitTaskMappingStatus(str, Enum):
    """
    Enumeration of possible commit-to-task mapping outcomes.

    Attributes:
        FOUND: A matching ClickUp task was successfully identified for the commit.
        NOT_FOUND: No ClickUp task matches the given commit.
        CLICK_UP_EMPTY: The ClickUp space contains no tasks to compare against.
    """
    FOUND = "FOUND"
    NOT_FOUND = "NOT_FOUND"
    CLICK_UP_EMPTY = "CLICK_UP_EMPTY"

class MappedCommitTaskResponse(BaseModel):
    """
    Representation of a commit-to-task mapping response.

    This DTO contains the result of attempting to associate a GitHub commit
    with a ClickUp task using semantic analysis.

    The response message may:
    - Confirm that a matching task was found
    - Inform the user that no matching task exists
    - Indicate that the ClickUp space contains no tasks

    Attributes:
        status: Outcome of the mapping operation.
        message: User-facing message describing the mapping result.
        task: The ClickUp task matched with the commit, if any.
    """
    status: CommitTaskMappingStatus = Field(..., description="Outcome of the commit-to-task mapping operation.")
    message: str = Field(
        ...,
        description=(
            "User-facing message describing the mapping result, "
            "such as success confirmation, no match notification, "
            "or empty workspace warning."
        )
    )
    task: Optional[ClickUpTask] = Field(default=None, description="The ClickUp task matched with the commit, if found.")