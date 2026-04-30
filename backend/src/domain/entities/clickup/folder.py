"""
Domain DTOs for ClickUp folder representation.

This module defines Data Transfer Objects (DTOs) used to represent ClickUp folders
and their associated lists. It provides a structured way to transfer hierarchical
ClickUp data between layers of the application.

Main classes:
    Folder
"""

from dataclasses import dataclass, field
from typing import List

from backend.src.domain.entities.clickup.clickup_list import ClickUpList


@dataclass
class Folder:
    """
    ClickUp folder containing multiple lists.

    This object represents a ClickUp folder and its associated lists,
    forming a hierarchical structure within a ClickUp space.

    Attributes:
        id: ClickUp folder identifier.
        name: Folder name.
        lists: List of ClickUp lists contained in the folder.
    """
    id: str
    name: str
    lists: List[ClickUpList] = field(default_factory=list)