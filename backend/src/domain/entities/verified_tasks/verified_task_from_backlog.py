"""
Domain DTOs for verified backlog task representation.

This module defines Data Transfer Objects (DTOs) used to represent
the results of task verification processes for backlog-generated tasks.
It provides structured models for transferring verification decisions,
such as task creation or update, along with associated metadata.

Main classes:
    VerifiedTaskFromBacklog, VerifiedTaskListFromBacklog
"""

from typing import List
from pydantic import BaseModel

from backend.src.domain.entities.verified_tasks.base_verified_task import BaseVerifiedTask


class VerifiedTaskFromBacklog(BaseVerifiedTask):
    """
    Representation of a verified backlog task.

    This DTO extends the base verified task model by adding an estimation
    field representing the expected effort or duration for the task.
    """
    estimation: int


class VerifiedTaskListFromBacklog(BaseModel):
    """
    Container for a list of verified backlog tasks.

    This DTO is used to transfer multiple verification results
    as a single structured object during backlog processing.

    Attributes:
        results: List of verified backlog tasks.
    """
    results: List[VerifiedTaskFromBacklog] = []