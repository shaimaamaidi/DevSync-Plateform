"""
Domain DTO for stale task inspection results.

This module defines DTOs used to represent the output of a stale task
analysis process. It is typically used after evaluating whether ClickUp
tasks are blocked or inactive based on contextual signals.

Main classes:
    InspectedStaleTaskResult
    InspectedStaleTaskListResult
"""

from typing import List

from pydantic import BaseModel


class InspectedStaleTaskResult(BaseModel):
    """
    Representation of a single inspected stale task.

    This DTO captures the analysis result for a task that may be
    considered stale or blocked based on heuristic or LLM-based inspection.

    Attributes:
        task_id: Identifier of the ClickUp task.
        task_name: Name of the ClickUp task.
        task_description: Description of the ClickUp task.
        is_blocked: Indicates whether the task is considered blocked.
        reason: Explanation of why the task is considered stale or not.
        confidence: Confidence level of the analysis
            ("high", "medium", or "low").
    """
    task_id: str
    task_name: str
    task_description: str
    is_blocked: bool
    reason: str
    confidence: str  # "high" | "medium" | "low"


class InspectedStaleTaskListResult(BaseModel):
    """
    Container DTO for multiple stale task inspection results.

    This class aggregates the results of stale task analysis
    across multiple ClickUp tasks.

    Attributes:
        tasks: List of inspected stale task results.
    """
    tasks: List[InspectedStaleTaskResult] = []