"""
Domain DTO for project status check requests.

This module defines the CheckedProjectStatusRequest DTO used to represent
a request for evaluating the status of a project based on ClickUp data
and an optional source code repository.

It encapsulates the ClickUp space identifier and optionally a GitHub
(or other VCS) repository URL used to enrich project status analysis.

Main classes:
    CheckedProjectStatusRequest
"""

from typing import Optional

from pydantic import BaseModel, Field


class CheckedProjectStatusRequest(BaseModel):
    """
    Representation of a project status check request.

    This DTO contains the required information to evaluate the current
    status of a project by combining ClickUp task data and optionally
    repository activity (commits, deployments, etc.).

    Attributes:
        space_id: Identifier of the ClickUp space where tasks are located and analyzed.
        repo_url: Optional URL of the source code repository associated with the project.
            If not provided, the status is based only on ClickUp data.
    """
    space_id: str = Field(..., min_length=1, description="Identifier of the ClickUp space where tasks should be searched.")
    repo_url: Optional[str] = Field(
        default=None,
        description="Optional URL of the source code repository related to the ClickUp space. Used to enrich status analysis with GitHub or VCS activity."
    )