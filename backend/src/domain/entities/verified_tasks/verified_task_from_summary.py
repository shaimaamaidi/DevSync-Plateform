"""
Domain DTOs for task verification result representation (summary-based tasks).

This module defines Data Transfer Objects (DTOs) used to represent the outcomes
of task verification processes for tasks generated from meeting summaries.
It provides a structured format for transferring decisions such as task creation
or update between application layers.

Main classes:
    VerifiedTaskFromSummary, VerifiedTaskListFromSummary
"""

from typing import List
from pydantic import BaseModel

from backend.src.domain.entities.verified_tasks.base_verified_task import BaseVerifiedTask


class VerifiedTaskFromSummary(BaseVerifiedTask):
    """
    Representation of a verified task from a meeting summary.

    This DTO extends the base verified task model and represents the result
    of verifying a task generated from a meeting summary (create or update decision).
    """
    pass


class VerifiedTaskListFromSummary(BaseModel):
    """
    Container for a list of verified tasks from meeting summaries.

    This DTO is used to transfer multiple verification results
    as a single structured object during processing workflows.

    Attributes:
        results: List of verified tasks from meeting summaries.
    """
    results: List[VerifiedTaskFromSummary] = []