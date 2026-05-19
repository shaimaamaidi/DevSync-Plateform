"""
Domain DTOs for epic representation.

This module defines Data Transfer Objects (DTOs) for managing epics in the backlog system.
An epic represents a high-level feature or business objective, and can be grouped into a list
for backlog generation or processing.

Main classes:
    Epic, EpicList
"""

from pydantic import BaseModel
from typing import List


class Epic(BaseModel):
    """
    Representation of a backlog epic.

    An epic is a high-level requirement or feature that groups multiple user stories
    in the backlog structure.

    Attributes:
        title: Title of the epic.
        description: Detailed description of the epic.
    """
    title: str
    description: str

class EpicList(BaseModel):
    """
    Container for a list of epics.

    This DTO is used to transfer multiple epics as a single structured object,
    typically during backlog generation or aggregation processes.

    Attributes:
        epics: List of epic entities.
    """
    epics: List[Epic] = []