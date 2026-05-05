"""
Domain DTOs for ClickUp list metadata representation.

This module defines Data Transfer Objects (DTOs) used to represent ClickUp lists
and their configuration metadata. It provides a structured way to transfer
ClickUp configuration data between layers of the application.

Main classes:
    ClickUpListMetadata
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class ClickUpListMetadata:
    """
    ClickUp list containing configuration metadata.

    This object represents a ClickUp list along with its available
    statuses and priority options.

    Attributes:
        id: ClickUp list identifier.
        name: List name.
        statuses: List of available task statuses in the list.
        priorities: List of available task priority levels.
    """
    id: str
    name: str
    statuses: List[str] = field(default_factory=list)
    priorities: List[str] = field(default_factory=list)