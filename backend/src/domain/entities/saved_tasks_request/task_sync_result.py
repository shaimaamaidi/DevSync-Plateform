"""
Domain DTOs for task synchronization results.

This module defines DTOs used to represent the outcome of task synchronization
operations with external systems.

Main classes:
    FailedTask: Information about a task that could not be synchronized.
    TaskSyncResult: Summary of a synchronization operation, including success,
        skip, and failure statistics.
"""

from dataclasses import field
from typing import List

from pydantic import BaseModel


class FailedTask(BaseModel):
    """
    Representation of a task synchronization failure.

    This DTO contains information about a task that could not be created
    or updated during a synchronization operation, along with the reason
    for the failure.

    Attributes:
        task_name: Name of the task that failed to synchronize.
        action: Synchronization action that failed ("create" or "update").
        reason: Description of the failure cause.
    """
    task_name: str
    action: str
    reason: str

class TaskSyncResult(BaseModel):
    """
    Summary of a task synchronization operation.

    This DTO aggregates synchronization statistics and provides details
    about tasks that could not be processed successfully.

    Attributes:
        total: Total number of tasks processed.
        created: Number of tasks successfully created.
        updated: Number of tasks successfully updated.
        failed: Number of tasks that failed to synchronize.
        failed_tasks: List of task synchronization failures.
    """
    total: int
    created: int
    updated: int
    failed: int
    failed_tasks: List[FailedTask] = field(default_factory=list)