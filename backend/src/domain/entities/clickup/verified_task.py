"""
Domain DTOs for task verification result representation.

This module defines Data Transfer Objects (DTOs) used to represent the outcomes
of task verification processes. It provides a structured format for transferring
decisions such as task creation or update between layers of the application.

Main classes:
    VerificationResult, VerificationResultList
"""

from typing import Optional, Literal, List
from pydantic import BaseModel


class VerifiedTask(BaseModel):
    """
    Result of a task verification decision.

    This object represents the outcome of verifying a task against existing data,
    indicating whether the task should be created or updated along with its metadata.

    Attributes:
        action: Action type, either "create" or "update".
        task_name: Name or title of the task.
        task_description: Detailed description of the task.
        task_assigne: Assignee name(s) as a string.
        task_status: Target status for the task.
        task_priority: Target priority level for the task.
        folder: Target folder name.
        task_id: Identifier of the existing task, if action is "update".
    """
    action: Literal["create", "update"]
    task_name: str
    task_description: str
    task_assigne: str
    task_status: str
    task_priority: str
    folder: str
    task_id: Optional[str] = None  # Only set when action == "update"


class VerifiedTaskList(BaseModel):
    """
    Collection of task verification results.

    This object represents a list of verification outcomes,
    typically returned as a batch for further processing.

    Attributes:
        results: List of verification results.
    """
    results: List[VerifiedTask]