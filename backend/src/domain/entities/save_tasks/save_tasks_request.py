"""
Domain DTO for ClickUp task saving request.

This module defines the input structure used to persist verified tasks into ClickUp.
It represents the final step of the workflow where tasks are either created or updated
based on prior verification results.

Main class:
    SaveTasksRequest
"""

from typing import List
from pydantic import BaseModel, Field

from backend.src.domain.entities.verify_tasks.verified_task import VerifiedTask


class SaveTasksRequest(BaseModel):
    """
    Representation of a request to save verified tasks into ClickUp.

    This DTO is used to apply verified tasks into a ClickUp workspace.
    It includes options to control assignee resolution behavior during persistence.

    Attributes:
        space_id: Identifier of the ClickUp workspace where tasks will be saved.
        tasks: List of verified tasks to be persisted in ClickUp.
        ignore_names: If True, ignores assignee names that do not exist in the database.
        ignore_mails: If True, ignores unresolved or invalid email-based assignments.
    """
    space_id: str = Field(..., description="Identifier of the ClickUp workspace.")
    tasks: List[VerifiedTask] = Field(..., description="List of verified tasks to be saved into ClickUp.")
    ignore_names: bool = Field(default=False, description="If True, ignores assignee names that do not exist in the database.")
    ignore_mails: bool = Field(default=False, description="If True, ignores unresolved email assignments.")