"""
Domain DTO for ClickUp status representation.

This module defines the ClickUpStatus data structure used to represent
task statuses within a ClickUp list.

It provides a structured way to model ClickUp workflow states (open,
custom, closed) and ensures consistent transformation of status data
when communicating with the ClickUp API.

Main components:
    StatusType, ClickUpStatus
"""

from dataclasses import dataclass
from enum import Enum


class StatusType(str, Enum):
    """
    ClickUp status type enumeration.

    Defines the lifecycle category of a task status in ClickUp:

    - OPEN   : Initial or starting status (e.g. "To Do")
    - CUSTOM : Intermediate workflow status (e.g. "In Progress", "Review")
    - CLOSED : Final terminal status (e.g. "Done")

    Notes:
        - ClickUp always enforces exactly one CLOSED status per list.
        - CLOSED status typically represents completion and cannot be removed,
          only renamed in most workspace configurations.
    """
    OPEN = "open"
    CUSTOM = "custom"
    CLOSED = "closed"


@dataclass
class ClickUpStatus:
    """
    Domain DTO representing a ClickUp list status configuration.

    A status defines a workflow step for tasks within a ClickUp list,
    including its display properties and lifecycle category.

    Attributes:
        status: Display name of the status (e.g. "In Progress").
        color: Hexadecimal color code associated with the status (e.g. "#4169e1").
        type: Lifecycle category of the status (OPEN / CUSTOM / CLOSED).
    """
    status: str
    color: str
    type: StatusType

    def to_dict(self) -> dict:
        """
        Convert the status into a ClickUp API-compatible payload.

        Returns:
            dict: Serialized representation used in ClickUp API requests.
        """
        return {
            "status": self.status,
            "color": self.color,
            "type": self.type.value,
        }