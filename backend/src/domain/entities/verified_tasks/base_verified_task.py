"""
Domain DTO for verified task decision result.

This module defines the data structure used to represent the outcome
of a task verification process. It indicates whether a task should be
created or updated, along with all relevant task metadata.

Main class:
    BaseVerifiedTask
"""

from typing import Literal, Optional

from pydantic import BaseModel


class BaseVerifiedTask(BaseModel):
    """
    Representation of a verified task decision result.

    This DTO is used after a verification step that determines whether
    a task should be created or updated in the system.

    Attributes:
        action: Operation to perform ("create" or "update").
        task_name: Name or title of the task.
        task_description: Detailed description of the task.
        task_assignee: Assignee name(s) as a string.
        task_status: Target status for the task.
        task_priority: Priority level assigned to the task.
        location: Target location where the task is managed.
        task_id: Identifier of the existing task (required when action is "update").
    """
    action: Literal["create", "update"]
    task_name: str
    task_description: str
    task_assignee: str
    task_status: str
    task_priority: str
    location: str
    task_id: Optional[str] = None  # Only set when action == "update"