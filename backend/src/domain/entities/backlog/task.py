"""
Domain DTOs for task representation.

This module defines Data Transfer Objects (DTOs) for managing tasks within the backlog system.
A task represents a small, actionable unit derived from a user story, and can be grouped into
a list associated with a specific user story.

Main classes:
    Task, TaskList
"""

from pydantic import BaseModel
from typing import List


class Task(BaseModel):
    """
    Representation of a task in the backlog.

    A task is a fine-grained unit of work derived from a user story, intended to be
    actionable and implementable by a developer.

    Attributes:
        title: Title of the task.
        description: Detailed description of the task.
    """
    title: str
    description: str

class TaskList(BaseModel):
    """
    Container for a list of tasks associated with a user story.

    This DTO groups multiple tasks under a specific user story for structured backlog representation.

    Attributes:
        user_story_title: Title of the related user story.
        tasks: List of tasks belonging to the user story.
    """
    user_story_title: str
    tasks: List[Task]