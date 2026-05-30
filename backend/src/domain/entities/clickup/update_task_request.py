"""
Domain DTO for task update requests.

This module defines the UpdateTaskRequest DTO used to encapsulate
data required to update a task in the ClickUp domain. It standardizes
the structure of update operations across application layers.

Main classes:
    UpdateTaskRequest
"""
from typing import Optional

from pydantic import BaseModel, Field


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
        estimation: Estimated duration in hours.
    """
    space_id: str = Field(..., min_length=1, description="Identifier of the task's space.")
    task_id: str = Field(..., min_length=1, description="Identifier of the task to update.")
    name: str = Field(..., min_length=1, description="Updated task name.")
    description: str = Field(..., min_length=1, description="Updated task description.")
    status: str = Field(..., min_length=1, description="New task status.")
    priority: Optional[str] = Field(None, description="Task priority level (optional).")
    assignees: Optional[str] = Field(None, description="New assignees (emails separated by commas).")
    old_assignees: Optional[str] = Field(None, description="Previous assignees (emails separated by commas).")
    ignore_mails: bool = Field(False, description="If True, email notifications will be ignored during update.")
    estimation: Optional[float] = Field(None, description="Estimated duration in hours, if any.")
