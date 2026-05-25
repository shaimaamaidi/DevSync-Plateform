"""
Domain DTOs for unverified completed task inspection.

This module defines DTOs used to represent completed tasks
that could not be verified through linked GitHub commit activity.

These DTOs are mainly used during project health analysis
to identify tasks marked as completed without sufficient
technical evidence of implementation.

Main classes:
    InspectedUnverifiedDoneTaskResult, InspectedUnverifiedDoneTaskListResult
"""

from typing import List

from pydantic import BaseModel


class InspectedUnverifiedDoneTaskResult(BaseModel):
    """
    Representation of an inspected completed task without verified commit activity.

    Attributes:
        task_id: Unique identifier of the task.
        task_name: Human-readable name of the task.
        task_description: Detailed description of the task.
        has_commit: Indicates whether related commit activity was found.
        reason: Explanation describing why the task is considered unverified.
        confidence: Confidence level of the inspection result (e.g., "high", "medium", "low").
    """
    task_id: str
    task_name: str
    task_description: str
    has_commit: bool
    reason: str
    confidence: str  # "high" | "medium" | "low"


class InspectedUnverifiedDoneTaskListResult(BaseModel):
    """
    Collection of inspected unverified completed tasks.

    Attributes:
        tasks: List of completed tasks identified as lacking verified implementation evidence.
    """
    tasks: List[InspectedUnverifiedDoneTaskResult] = []