"""
Domain DTOs for ClickUp list representation with tasks.

This module defines Data Transfer Objects (DTOs) used to represent ClickUp lists
along with their associated tasks and configuration metadata. It provides a
structured way to transfer complete ClickUp list data between layers of the application.

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

    This object represents a complete ClickUp list, including its tasks
    and configuration data such as available statuses and priority options.

    Attributes:
        id: ClickUp list identifier.
        name: List name.
        tasks: List of tasks contained in the list.
        statuses: List of available task statuses in the list.
        priorities: List of available task priority levels.
    """
    id: str
    name: str
    tasks: List[ClickUpTask] = field(default_factory=list)
    statuses: List[str] = field(default_factory=list)
    priorities: List[str] = field(default_factory=list)