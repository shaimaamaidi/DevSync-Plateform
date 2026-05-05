"""
Domain DTOs for ClickUp folder metadata representation.

This module defines Data Transfer Objects (DTOs) used to represent ClickUp folders
and their associated lists metadata. It provides a structured way to transfer
hierarchical ClickUp configuration data between layers of the application.

Main classes:
    FolderWithListsMetadata
"""

from dataclasses import dataclass, field
from typing import List

from backend.src.domain.entities.clickup.list_metadata import ClickUpListMetadata


@dataclass
class FolderWithListsMetadata:
    """
    ClickUp folder containing multiple lists metadata.

    This object represents a ClickUp folder and its associated lists metadata,
    forming a hierarchical configuration structure within a ClickUp space.

    Attributes:
        id: ClickUp folder identifier.
        name: Folder name.
        lists: List of ClickUp lists metadata contained in the folder.
    """
    id: str
    name: str
    lists: List[ClickUpListMetadata] = field(default_factory=list)