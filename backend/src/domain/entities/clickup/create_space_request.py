"""
Domain DTO for creating or referencing a ClickUp space.

This module defines the CreateSpaceRequest data transfer object (DTO), which is used
to encapsulate the information required to create or initialize operations on a ClickUp
space. It provides a structured way to transfer space-related data between application layers.

Main classes:
    CreateSpaceRequest
"""

from pydantic import BaseModel


class CreateSpaceRequest(BaseModel):
    """
    Request model for creating or referencing a ClickUp space.

    This DTO represents the payload required to identify a ClickUp space for further
    operations such as folder or list creation. It mainly carries the space identifier.

    Attributes:
        space_name: ClickUp space name.
    """
    space_name: str
