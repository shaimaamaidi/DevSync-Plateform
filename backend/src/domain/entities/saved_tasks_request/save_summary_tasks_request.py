"""
Domain DTO for summary tasks saving in click up request.

This module defines the input structure used to persist verified summary tasks into ClickUp.
It represents the final step of the workflow where tasks are either created or updated
based on prior verification results.

Main class:
    SaveSummaryTasksRequest
"""

from typing import List
from pydantic import BaseModel, Field

from backend.src.domain.entities.verified_tasks.verified_task_from_summary import VerifiedTaskFromSummary


class SaveSummaryTasksRequest(BaseModel):
    """
    Representation of a request to save verified summary tasks into ClickUp.

    This DTO is used to apply verified summary tasks into a ClickUp workspace.
    It includes options to control assignee resolution behavior during persistence.

    Attributes:
        space_id: Identifier of the ClickUp workspace where tasks will be saved.
        tasks: List of verified tasks to be persisted in ClickUp.
        ignore_names: If True, ignores assignee names that do not exist in the database.
        ignore_mails: If True, ignores unresolved or invalid email-based assignments.
    """
    space_id: str = Field(..., min_length=1, description="Identifier of the ClickUp workspace.")
    tasks: List[VerifiedTaskFromSummary] = Field(..., description="List of verified tasks that are generated from a summary meeting to be saved into ClickUp.")
    ignore_names: bool = Field(default=False, description="If True, ignores assignee names that do not exist in the database.")
    ignore_mails: bool = Field(default=False, description="If True, ignores unresolved email assignments.")