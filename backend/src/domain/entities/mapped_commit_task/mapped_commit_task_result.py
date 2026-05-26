"""
Domain DTO for commit-to-task mapping result.

This module defines the DTO used to represent the result of mapping
a Git commit message to a single ClickUp task ID.

Main classes:
    CommitTaskMapperResult
"""

from typing import Optional

from pydantic import BaseModel


class CommitTaskMapperResult(BaseModel):
    """
    Representation of a commit-to-task mapping result.

    This DTO contains the ID of the single ClickUp task that best
    matches a given Git commit message, as returned by the LLM.

    Attributes:
        id: ClickUp task identifier, or None if no match was found.
    """
    id: Optional[str] = None