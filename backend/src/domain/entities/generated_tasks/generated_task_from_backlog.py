"""
Domain DTOs for generated backlog task representation.

This module defines Data Transfer Objects (DTOs) used to represent
tasks generated from a backlog by the AI system. Each generated task
extends the base generated task structure with an estimation field,
and tasks can be grouped into a list container for processing or transfer.

Main classes:
    GeneratedTaskFromBacklog, GeneratedTaskListFromBacklog
"""

from typing import List

from pydantic import BaseModel

from backend.src.domain.entities.generated_tasks.base_generated_task import BaseGeneratedTask


class GeneratedTaskFromBacklog(BaseGeneratedTask):
    """
    Representation of a generated backlog task.

    This DTO extends the base generated task model by adding
    an estimation value representing the expected effort or duration.

    Attributes:
        estimation: Estimated effort or duration for the task.
    """
    estimation: int


class GeneratedTaskListFromBacklog(BaseModel):
    """
    Container for a list of generated backlog tasks.

    This DTO is used to transfer multiple generated tasks
    as a single structured object during backlog generation
    or task aggregation processes.

    Attributes:
        tasks: List of generated backlog tasks.
    """
    tasks: List[GeneratedTaskFromBacklog] = []