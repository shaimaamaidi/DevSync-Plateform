"""
Domain DTOs for LLM-generated task representation.

This module defines Data Transfer Objects (DTOs) used to represent tasks generated
from meeting summaries by an LLM. It provides a structured format for transferring
generated task data between layers of the application.

Main classes:
    GeneratedTask, TaskList
"""

from dataclasses import dataclass
from typing import List

from pydantic import BaseModel


@dataclass
class GeneratedTask(BaseModel):
    """
    Task generated from a meeting summary.

    This object represents a task inferred by an LLM, including its metadata
    such as description, assignment, status, and target location.

    Attributes:
        task_name: Name or title of the task.
        task_description: Detailed description of the task.
        task_assigne: Assignee name(s) as a string.
        task_status: Target status for the task.
        task_priority: Target priority level for the task.
        folder: Target folder name where the task should be created.
    """
    task_name: str
    task_description: str
    task_assigne: str
    task_status: str
    task_priority: str
    folder: str


class GeneratedTaskList(BaseModel):
    """
    Collection of generated tasks.

    This object represents a list of tasks produced by the LLM,
    typically returned as a batch for further processing or integration.

    Attributes:
        tasks: List of generated tasks.
    """
    tasks: List[GeneratedTask]