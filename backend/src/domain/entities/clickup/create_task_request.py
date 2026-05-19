"""
Domain DTO for task creation requests.

This module defines the CreateTaskRequest DTO used to encapsulate
data required to create a task in the ClickUp domain. It standardizes
the structure of task creation operations across application layers.

Main classes:
    CreateTaskRequest
"""
from typing import Optional

from pydantic import BaseModel


class CreateTaskRequest(BaseModel):
    """
    Request payload used to create a ClickUp task.

    This DTO contains all necessary information to create a new task
    within a specific list and space, including metadata, assignment
    details, and notification control.

    Attributes:
        space_id: Identifier of the ClickUp space containing the list.
        list_id: Identifier of the ClickUp list where the task will be created.
        name: Task name.
        description: Task description.
        status: Initial task status.
        priority: Task priority level (optional).
        assignees: Assignees (emails separated by commas).
        ignore_mails: If True, email notifications will be ignored during creation.
    """
    space_id: str
    list_id: str
    name: str
    description: str
    status: Optional[str] = None
    priority: Optional[str] = None
    assignees: Optional[str] = None  # comma-separated emails
    ignore_mails: bool = False