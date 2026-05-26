"""
Domain DTO for task search and mapping results.

This module defines the TaskSearchResult DTO used to represent
the result of semantic search or LLM-based mapping of ClickUp tasks.

It aggregates task identifiers returned by AI agents that perform:
- Semantic task search within ClickUp spaces
- Commit-to-task mapping based on Git commit messages

Main classes:
    TaskSearchResult
"""

from typing import List
from pydantic import BaseModel


class TaskSearchResult(BaseModel):
    """
    Representation of task search/matching results.

    This DTO contains the list of ClickUp task identifiers returned
    by an LLM-based search or mapping process.

    It is used to represent the output of agents responsible for:
    - Semantic task search (TaskSearchAgent)
    - Commit-to-task mapping (CommitTaskMapperAgent)

    Attributes:
        ids: List of matched ClickUp task identifiers.
    """
    ids: List[str] = []