"""
Domain DTO for task creation requests.

This module defines the CreateTaskRequest DTO used to encapsulate
data required to create a task in the ClickUp domain. It standardizes
the structure of task creation operations across application layers.

Main classes:
    CreateTaskRequest
"""
from typing import Optional

from pydantic import BaseModel, Field


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
        estimation: Estimated duration in hours.
    """
    space_id: str = Field(..., min_length=1, description="Identifier of the ClickUp space containing the list.")
    list_id: str = Field(..., min_length=1, description="Identifier of the ClickUp list where the task will be created.")
    name: str = Field(..., min_length=1, description="Task name.")
    description: str = Field(..., min_length=1, description="Task description.")
    status: Optional[str] = Field(None, description="Initial task status.")
    priority: Optional[str] = Field(None, description="Task priority level (optional).")
    assignees: Optional[str] = Field(None, description="Assignees (emails separated by commas).")
    ignore_mails: bool = Field(False, description="If True, email notifications will be ignored during creation.")
    estimation: Optional[float] = Field(None, description="Estimated duration in hours, if any.")
