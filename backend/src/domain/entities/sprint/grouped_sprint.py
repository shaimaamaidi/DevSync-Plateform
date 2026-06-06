"""
Domain DTO for sprint grouping results.

This module defines DTOs used to represent a structured grouping of backlog items into sprints.
It is typically used by sprint planning agents to organize user stories into coherent sprint units
based on logical grouping, workload distribution, and business goals.

Main classes:
    SprintGroup, SprintGrouping
"""

from typing import List
from pydantic import BaseModel


class SprintGroup(BaseModel):
    """
    Representation of a single sprint group.

    A sprint group contains a set of user stories grouped together
    with a shared goal and an estimated workload.

    Attributes:
        name: Name of the sprint (e.g., "Sprint 1 - Authentication").
        goal: Objective or business goal of the sprint.
        total_estimated_hours: Total estimated effort for all stories in the sprint.
        story_ids: List of user story identifiers included in this sprint.
    """
    name: str
    goal: str
    total_estimated_hours: float
    story_ids: List[str]

class SprintGrouping(BaseModel):
    """
    Result of sprint grouping process.

    This DTO represents the full output of a sprint planning operation,
    containing multiple sprint groups.

    Attributes:
        sprints: List of generated sprint groups.
    """
    sprints: List[SprintGroup] = []