"""
Domain DTO for task search results.

This module defines the TaskSearchResult DTO used to represent the result of a task search operation.
It encapsulates a collection of ClickUp tasks matching a given search query or filtering criteria.

Main classes:
    TaskSearchResult
"""

from typing import List

from pydantic import BaseModel

from backend.src.domain.entities.clickup.list_with_tasks import ClickUpTask


class TaskSearchResult(BaseModel):
    """
    Representation of task search results.

    This DTO contains the list of ClickUp tasks returned after performing
    a search operation within folders, lists, or other task collections.

    Attributes:
        tasks: List of ClickUp tasks matching the search criteria.
    """
    tasks: List[ClickUpTask]