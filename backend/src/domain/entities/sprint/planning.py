"""
Domain DTO for sprint planning structure.

This module defines the SprintPlanning DTO used to represent a complete sprint planning output.
It aggregates multiple sprints, each containing user stories and task estimations, to form a
structured delivery plan for the project.

Main classes:
    SprintPlanning
"""

from pydantic import BaseModel
from typing import List

from backend.src.domain.entities.sprint.sprint import Sprint
from backend.src.domain.entities.sprint.sprint_with_identified_tasks import SprintWithTaskIdentified


class SprintPlanning(BaseModel):
    """
    Container for sprint planning results.

    This DTO represents the full sprint breakdown of a project, including all planned sprints
    and their associated user stories and task estimations.

    Attributes:
        sprints: List of planned sprints.
    """
    sprints: List[Sprint] = []

class SprintPlanningWithTaskIdentified(BaseModel):
    """
    Container for sprint planning results.

    This DTO represents the full sprint breakdown of a project, including all planned sprints
    and their associated user stories and task estimations.

    Attributes:
        sprints: List of planned sprints.
    """
    sprints: List[SprintWithTaskIdentified] = []