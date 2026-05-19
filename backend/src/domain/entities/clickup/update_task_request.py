"""
Domain DTO for task update requests.

This module defines the UpdateTaskRequest DTO used to encapsulate
data required to update a task in the ClickUp domain. It standardizes
the structure of update operations across application layers.

Main classes:
    UpdateTaskRequest
"""
from typing import Optional

from pydantic import BaseModel


class UpdateTaskRequest(BaseModel):
    """
    Request payload used to update a ClickUp task.

    This DTO contains all information required to modify an existing task,
    including metadata updates, assignment changes, and control flags.

    Attributes:
        space_id: Identifier of the task's space.
        task_id: Identifier of the task to update.
        name: Updated task name.
        description: Updated task description.
        status: New task status.
        priority: Task priority level (optional).
        assignees: New assignees (emails separated by commas).
        old_assignees: Previous assignees (emails separated by commas).
        ignore_mails: If True, email notifications will be ignored during update.
    """
    space_id: str
    task_id: str
    name: str
    description: str
    status: str
    priority: Optional[str] = None
    assignees: Optional[str] = None      # new assignees (comma-separated emails)
    old_assignees: Optional[str] = None  # previous assignees (comma-separated emails)
    ignore_mails: bool = False