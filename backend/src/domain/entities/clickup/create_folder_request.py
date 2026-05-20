"""
Domain DTO for creating a ClickUp folder.

This module defines the CreateFolderRequest data transfer object (DTO), which is used
to encapsulate the information required to create a new folder inside a ClickUp space.
It provides a structured way to transfer folder creation data between application layers.

Main classes:
    CreateFolderRequest
"""

from pydantic import BaseModel, Field


class CreateFolderRequest(BaseModel):
    """
    Request model for creating a ClickUp folder.

    This DTO represents the payload required to create a new folder in a specific
    ClickUp space. It contains the target space identifier and the folder name.

    Attributes:
        space_id: ClickUp space identifier where the folder will be created.
        name: Name of the folder to create.
    """
    space_id: str = Field(..., min_length=1, description="ClickUp space identifier where the folder will be created.")
    name: str = Field(..., min_length=1, description="Name of the folder to create.")