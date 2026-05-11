"""
Domain DTOs for task representation.

This module defines the Task data structure used to represent
task information exchanged across the application domain.

The Task DTO encapsulates the core attributes required for
task creation, update, and synchronization with external
providers such as ClickUp.

It provides a consistent structure for transporting task
metadata between application layers.

Main components:
    Task
"""
from typing import Optional

from pydantic import BaseModel


class Task(BaseModel):
    """
    Domain DTO representing a task entity.

    A task contains the essential information required for
    workflow management and synchronization with external
    task management systems.

    Attributes:
        task_name: Human-readable task title.
        task_description: Detailed task description or content.
        task_assigne: Comma-separated list of assignee identifiers
        task_status: Workflow status associated with the task
        task_priority: Priority level assigned to the task
        task_id: Optional external task identifier. This field is mainly
            populated when retrieving tasks from ClickUp through reader adapters.
    """

    task_name: str
    task_description: str
    task_assigne: str
    task_status: str
    task_priority: str
    task_id: Optional[str] = None # Only with get_tasks dans click up reader