"""
Domain DTO for creating a ClickUp list.

This module defines the CreateListRequest data transfer object (DTO), which is used
to encapsulate the information required to create a new list inside a ClickUp space
or folder. It provides a structured way to transfer list creation data between
application layers.

Main classes:
    CreateListRequest
"""

from typing import Optional

from pydantic import BaseModel, Field


class CreateListRequest(BaseModel):
    """
    Request model for creating a ClickUp list.

    This DTO represents the payload required to create a new list in a ClickUp space.
    The list can optionally be created inside a specific folder. If no folder is
    provided, the list is created directly under the space.

    Attributes:
        space_id: ClickUp space identifier where the list will be created.
        name: Name of the list to create (default is "List").
        folder_id: Optional folder identifier if the list is created inside a folder.
    """
    space_id: str = Field(..., min_length=1, description="ClickUp space identifier where the list will be created.")
    name: str = Field("List", min_length=1, description="Name of the list to create.")
    folder_id: Optional[str] = Field(None, description="Optional folder identifier if the list is created inside a folder.")