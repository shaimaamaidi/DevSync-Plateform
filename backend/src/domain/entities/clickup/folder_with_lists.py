"""
Domain DTOs for ClickUp folder representation with lists and tasks.

This module defines Data Transfer Objects (DTOs) used to represent ClickUp folders
along with their associated lists and tasks. It provides a structured way to transfer
complete hierarchical ClickUp data between layers of the application.

Main classes:
    FolderWithLists, FolderWithListsAndEstimation
"""

from typing import List

from pydantic import BaseModel

from backend.src.domain.entities.clickup.list_with_tasks import ClickUpList, ClickUpListWithEstimation


class FolderWithLists(BaseModel):
    """
    ClickUp folder containing multiple lists with tasks.

    This object represents a complete ClickUp folder, including its lists
    and their associated tasks, forming a hierarchical structure within a ClickUp space.

    Attributes:
        id: ClickUp folder identifier.
        name: Folder name.
        lists: List of ClickUp lists (with tasks) contained in the folder.
    """
    id: str
    name: str
    lists: List[ClickUpList] = []

class FolderWithListsAndEstimation(BaseModel):
    """
    ClickUp folder containing multiple lists with tasks and estimations.

    Extends the base folder structure to include estimation data
    on each task.

    Attributes:
        id: ClickUp folder identifier.
        name: Folder name.
        lists: List of ClickUp lists (with tasks and estimations).
    """
    id: str
    name: str
    lists: List[ClickUpListWithEstimation] = []