"""
Domain DTOs for user story representation.

This module defines Data Transfer Objects (DTOs) for managing user stories within the backlog system.
A user story represents a functional requirement derived from an epic and can be further decomposed
into tasks for implementation.

Main classes:
    UserStory, UserStoryList
"""

from pydantic import BaseModel
from typing import List


class UserStory(BaseModel):
    """
    Representation of a user story in the backlog.

    A user story describes a functional requirement from the end-user perspective
    and serves as an intermediate level between epics and tasks.

    Attributes:
        title: Title of the user story.
        description: Detailed description of the user story.
    """
    title: str
    description: str

class UserStoryList(BaseModel):
    """
    Container for a list of user stories associated with an epic.

    This DTO groups multiple user stories under a specific epic for structured backlog representation.

    Attributes:
        epic_title: Title of the related epic.
        user_stories: List of user stories belonging to the epic.
    """
    epic_title: str
    user_stories: List[UserStory] = []