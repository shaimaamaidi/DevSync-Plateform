"""
Domain DTO for sprint planning with identified task estimations.

This module defines DTOs used to represent sprints enriched with user stories
and their corresponding estimated tasks. It supports detailed sprint planning,
workload analysis, and traceability between user stories and tasks.

Main classes:
    UserStorySprintWithTaskIdentified, SprintWithTaskIdentified
"""

from typing import List
from pydantic import BaseModel

from backend.src.domain.entities.backlog.user_story import UserStory
from backend.src.domain.entities.sprint.estimation import IdentifiedEstimatedTask


class UserStorySprintWithTaskIdentified(BaseModel):
    """
    User story enriched with its identified estimated tasks.

    This DTO links a user story to its decomposed and estimated tasks,
    enabling fine-grained workload analysis at sprint level.

    Attributes:
        user_story: The user story included in the sprint.
        tasks: List of estimated tasks associated with the user story.
    """
    user_story: UserStory
    tasks: List[IdentifiedEstimatedTask] = []

class SprintWithTaskIdentified(BaseModel):
    """
    Sprint representation with detailed task-level estimation.

    This DTO groups multiple user stories and their estimated tasks,
    providing a full view of sprint scope, goal, and workload.

    Attributes:
        name: Name of the sprint (e.g., "Sprint 1 - Authentication").
        goal: Objective or business outcome of the sprint.
        total_estimated_hours: Total workload estimation in hours.
        user_stories: List of user stories with their associated tasks.
    """
    name: str
    goal: str
    total_estimated_hours: float
    user_stories: List[UserStorySprintWithTaskIdentified] = []