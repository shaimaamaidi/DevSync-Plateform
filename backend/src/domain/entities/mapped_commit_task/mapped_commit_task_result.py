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

    This DTO contains the ClickUp task that best matches a given
    Git commit message, along with the confidence score assigned
    by the mapping process.

    Attributes:
        id: ClickUp task identifier, or None if no suitable match was found.
        confidence: Confidence score between 0.0 and 1.0 indicating
            how strongly the commit is associated with the identified task,
            or None if no confidence score is available.
    """
    id: Optional[str] = None
    confidence: Optional[float] = None