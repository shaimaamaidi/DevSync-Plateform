"""
Domain DTOs for ClickUp list representation.

This module defines Data Transfer Objects (DTOs) used to represent ClickUp lists
and their associated tasks. It provides a structured way to transfer ClickUp data
between layers of the application.

Main classes:
    ClickUpTask, ClickUpList
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class ClickUpTask:
    """
    Task representation within a ClickUp list.

    Attributes:
        id: Task identifier.
        name: Task name or title.
        description: Task description.
        status: Current task status.
        assignee: Username of the assignee, if any.
        priority: Priority level of the task, if any.
    """
    id: str
    name: str
    description: str
    status: str
    assignee: str | None
    priority: str | None


@dataclass
class ClickUpList:
    """
    ClickUp list containing tasks and configuration metadata.

    This object represents a ClickUp list along with its tasks,
    available statuses, and priority options.

    Attributes:
        id: ClickUp list identifier.
        name: List name.
        tasks: List of tasks contained in the list.
        statuses: List of available statuses for tasks in the list.
        priorities: List of available priority levels for tasks in the list.
    """
    id: str
    name: str
    tasks: List[ClickUpTask] = field(default_factory=list)
    statuses: List[str] = field(default_factory=list)
    priorities: List[str] = field(default_factory=list)