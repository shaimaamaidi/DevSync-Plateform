"""
Domain DTO for adding a status to a ClickUp list.

This module defines the AddStatusRequest data transfer object (DTO), which is used
to encapsulate the information required to add a new status to a ClickUp list.
It provides a structured way to transfer status creation data between application layers.

Main classes:
    AddStatusRequest
"""

from pydantic import BaseModel

from backend.src.domain.entities.clickup.status import StatusType


class AddStatusRequest(BaseModel):
    """
    Request model for adding a status to a ClickUp list.

    This DTO represents the payload required to create a new status in a specific
    ClickUp list. It includes the target list identifier, the status label, its color,
    and its type (custom or predefined).

    Attributes:
        list_id: ClickUp list identifier where the status will be added.
        status: Name of the status to be created.
        color: Color associated with the status (typically hex or ClickUp color code).
        type: Type of the status (e.g., custom, open, closed).
    """
    list_id: str
    status: str
    color: str
    type: StatusType