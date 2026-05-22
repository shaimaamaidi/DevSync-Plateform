"""
Domain DTOs for generated meeting summary task representation.

This module defines Data Transfer Objects (DTOs) used to represent
tasks generated from meeting summaries by the AI system. It provides
structured models for transferring generated task data individually
or as grouped collections across application layers.

Main classes:
    GeneratedTaskFromSummary, GeneratedTaskListFromSummary
"""

from typing import List

from pydantic import BaseModel

from backend.src.domain.entities.generated_tasks.base_generated_task import BaseGeneratedTask


class GeneratedTaskFromSummary(BaseGeneratedTask):
    """
    Representation of a generated task from a meeting summary.

    This DTO extends the base generated task model and represents
    a task inferred from meeting summary content by the AI system.
    """
    pass


class GeneratedTaskListFromSummary(BaseModel):
    """
    Container for a list of generated tasks from meeting summaries.

    This DTO is used to transfer multiple generated tasks
    as a single structured object during task generation
    or aggregation processes.

    Attributes:
        tasks: List of generated tasks from meeting summaries.
    """
    tasks: List[GeneratedTaskFromSummary] = []