"""
Domain DTO for commit-to-task mapping requests.

This module defines the MappedCommitTaskRequest DTO used to represent
the input required to map a GitHub commit to a ClickUp task.

It encapsulates:
- The commit information to analyze
- The ClickUp space context where tasks are located

Main classes:
    MappedCommitTaskRequest
"""

from pydantic import BaseModel, Field


class MappedCommitTaskRequest(BaseModel):
    """
    Representation of a commit-to-task mapping request.

    This DTO contains the input data required to associate a GitHub commit
    with a ClickUp task using semantic analysis.

    Attributes:
        commit: GitHub commit message or identifier to analyze.
        space_id: ClickUp space identifier where tasks are located.
    """
    commit: str = Field(..., min_length=1, description="GitHub commit message or identifier to analyze.")
    space_id: str = Field(..., min_length=1, description="ClickUp space identifier where tasks are located.")