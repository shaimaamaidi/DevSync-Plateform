"""
Domain DTOs for sprint planning representation.

This module defines Data Transfer Objects (DTOs) used to structure sprint planning data.
A sprint groups user stories and their estimated tasks, along with a global sprint goal
and total estimated effort.

Main classes:
    UserStorySprint, UserStoriesList, Sprint
"""

from pydantic import BaseModel
from typing import List

from backend.src.domain.entities.backlog.user_story import UserStory
from backend.src.domain.entities.sprint.estimation import EstimatedTask


class UserStorySprint(BaseModel):
    """
    Representation of a user story within a sprint context.

    This DTO links a user story with its estimated tasks, allowing sprint-level planning
    and workload distribution.

    Attributes:
        user_story: User story included in the sprint.
        tasks: List of task estimations associated with the user story.
    """
    user_story: UserStory
    tasks: List[EstimatedTask] = []

class UserStoriesList(BaseModel):
    """
    Representation of a user story within a sprint context.

    This DTO links a user story with its estimated tasks, allowing sprint-level planning
    and workload distribution.

    Attributes:
        user_stories: User story included in the sprint.
    """
    user_stories: List[UserStorySprint]

class Sprint(BaseModel):
    """
    Representation of a sprint in the planning process.

    A sprint groups multiple user stories and defines a goal along with the total estimated effort.
    It is used for sprint planning, capacity estimation, and workload organization.

    Attributes:
        name: Name of the sprint.
        goal: Sprint objective or target outcome.
        total_estimated_hours: Total estimated effort in hours for the sprint.
        user_stories: List of user stories included in the sprint with task estimations.
    """
    name: str
    goal: str
    total_estimated_hours: float
    user_stories: List[UserStorySprint] = []
