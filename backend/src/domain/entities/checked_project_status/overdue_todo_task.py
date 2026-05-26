"""
Domain DTO for overdue Todo tasks.

This module defines the OverdueTodoTask DTO used to represent
a Todo task that has remained inactive for an extended period
without being started or updated.

It is mainly used in project health analysis to highlight
tasks that may require attention or prioritization.

Main classes:
    OverdueTodoTask
"""

from pydantic import BaseModel


class OverdueTodoTask(BaseModel):
    """
    Representation of an overdue Todo task.

    Attributes:
        task_id: Unique identifier of the task.
        task_name: Human-readable name of the task.
        task_description: Detailed description of the task.
        days_waiting: Number of days the task has remained in Todo status.
        reason: Explanation describing why the task is considered overdue.
    """
    task_id: str
    task_name: str
    task_description: str
    days_waiting: int
    reason: str