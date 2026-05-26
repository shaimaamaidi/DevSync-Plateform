"""
Shared base DTO for project space requests.

This module defines the ProjectSpaceRequest base DTO used to represent
any request targeting a ClickUp space with an optional source code repository.

Main classes:
    ProjectSpaceRequest
"""

from typing import Optional

from pydantic import BaseModel, Field


class ProjectSpaceRequest(BaseModel):
    """
    Base representation of a request targeting a ClickUp space.

    Attributes:
        space_id: Identifier of the ClickUp space where tasks are located and analyzed.
        repo_url: Optional URL of the source code repository associated with the project.
            If not provided, the analysis is based only on ClickUp data.
    """
    space_id: str = Field(..., min_length=1, description="Identifier of the ClickUp space where tasks should be searched.")
    repo_url: Optional[str] = Field(
        default=None,
        description="Optional URL of the source code repository related to the ClickUp space. Used to enrich analysis with GitHub or VCS activity."
    )