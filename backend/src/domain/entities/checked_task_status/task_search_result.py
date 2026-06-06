"""
Domain DTOs for task search and matching results.

This module defines DTOs used to represent the results of semantic
task search and LLM-based task matching operations.

The DTOs capture the ClickUp tasks identified by AI agents along
with confidence scores indicating the relevance of each match.

Main classes:
    TaskCandidate, TaskSearchResult
"""

from typing import List, Optional
from pydantic import BaseModel


class TaskCandidate(BaseModel):
    """
    Representation of a single task search result.

    This DTO contains a ClickUp task identifier returned by a search
    or matching process, together with a confidence score reflecting
    the relevance of the match.

    Attributes:
        id: ClickUp task identifier, or None if no task was identified.
        confidence: Confidence score between 0.0 and 1.0 indicating
            the relevance of the identified task, or None if no
            confidence score is available.
    """
    id: Optional[str] = None
    confidence: Optional[float] = None


class TaskSearchResult(BaseModel):
    """
    Representation of multiple task search results.

    This DTO contains a collection of task search results returned
    by an LLM-based search or matching process.

    It is typically used when multiple candidate tasks can be
    associated with a user query, requirement, or commit message.

    Attributes:
        candidates: List of identified task matches with their associated
            confidence scores.
    """
    candidates: List[TaskCandidate]