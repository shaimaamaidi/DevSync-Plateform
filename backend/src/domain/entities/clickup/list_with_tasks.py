"""
Domain DTOs for ClickUp list representation with tasks.

This module defines Data Transfer Objects (DTOs) used to represent ClickUp lists
along with their associated tasks and configuration metadata. It provides a
structured way to transfer complete ClickUp list data between layers of the application.

Main classes:
    ClickUpTask, ClickUpList, ClickUpTaskWithEstimation, ClickUpListWithEstimation
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class ClickUpTask(BaseModel):
    """
    Task representation within a ClickUp list.

    Attributes:
        id: Task identifier.
        name: Task name or title.
        description: Task description.
        status: Current task status.
        assignee: email of the assignee, if any.
        priority: Priority level of the task, if any.
    """
    id: Optional[str] = Field(None, description="Task identifier.")
    name: str = Field(..., min_length=1, description="Task name or title.")
    description: Optional[str] = Field(None, description="Task description.")
    status: Optional[str] = Field(None, description="Current task status.")
    assignee: Optional[str] = Field(None, description="Email of the assignee, if any.")
    priority: Optional[str] = Field(None, description="Priority level of the task, if any.")

    def to_dict(self) -> dict:
        """
        Serialize task fields for LLM consumption.
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "assignee": self.assignee,
        }


class ClickUpList(BaseModel):
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
    tasks: List[ClickUpTask] = []
    statuses: List[str] = []
    priorities: List[str] = []

class ClickUpTaskWithEstimation(ClickUpTask):
    """
    Task representation within a ClickUp list, including time estimation.

    Extends ClickUpTask with an estimation field representing the estimated
    duration of the task in hours.

    Attributes:
        estimation: Estimated duration in hours, if any.
    """
    estimation: Optional[float] = Field(None, description="Estimated duration in hours, if any.")

    def to_dict(self) -> dict:
        """
        Serialize task fields for LLM consumption, including estimation.
        """
        base = super().to_dict()
        base["estimation"] = self.estimation
        return base


class ClickUpListWithEstimation(ClickUpList):
    """
    ClickUp list containing tasks with estimation data.

    Extends ClickUpList by typing the tasks list as ClickUpTaskWithEstimation.

    Attributes:
        tasks: List of tasks with estimation contained in the list.
    """
    tasks: List[ClickUpTaskWithEstimation] = []