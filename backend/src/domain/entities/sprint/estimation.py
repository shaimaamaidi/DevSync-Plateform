"""
Domain DTO for task estimation.

This module defines the TaskEstimate DTO used to represent a task along with its estimated effort.
It is typically used during sprint planning to evaluate workload and distribute tasks across sprints.

Main classes:
    TaskEstimate
"""

from pydantic import BaseModel

from backend.src.domain.entities.backlog.task import Task


class TaskEstimate(BaseModel):
    """
    Representation of a task with its estimated effort.

    This DTO links a task to an estimation value in hours, enabling sprint planning,
    capacity management, and workload balancing.

    Attributes:
        task: Task entity to be estimated.
        estimated_hours: Estimated effort required to complete the task (in hours).
    """
    task: Task
    estimated_hours: float