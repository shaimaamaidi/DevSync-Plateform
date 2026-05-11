"""
Domain DTOs for ClickUp space data.

This module defines Data Transfer Objects (DTOs) for ClickUp space management, including creation,
update, retrieval, and association with repositories.

Main classes:
    ClickUpSpaceDTO, ClickUpSpaceCreateDTO, ClickUpSpaceRegisterDTO, ClickUpSpaceUpdateDTO,
    ClickUpSpaceLightDTO, ClickUpSpaceDetailDTO, ClickUpRepoDTO, ClickUpRepoRefDTO
"""

from typing import Optional
from pydantic import BaseModel


class ClickUpRepoDTO(BaseModel):
    """
    Repository details embedded in ClickUp space responses.

    Attributes:
        id: Repository identifier.
        name: Repository name.
        url: Repository URL.
    """
    id: Optional[int] = None
    name: Optional[str] = None
    url: Optional[str] = None

class ClickUpRepoRefDTO(BaseModel):
    """
    Reference to a repository linked to a ClickUp space.

    Attributes:
        id: Repository identifier.
        url: Repository URL.
    """
    id: Optional[int] = None
    url: Optional[str] = None

class ClickUpSpaceDTO(BaseModel):
    """
    ClickUp space DTO with minimal fields.

    Attributes:
        id: ClickUp space identifier.
        name: ClickUp space name.
        space_code: ClickUp space code.
    """
    id: Optional[int] = None
    name: Optional[str] = None
    space_code: Optional[str] = None


class ClickUpSpaceCreateDTO(BaseModel):
    """
    Payload for ClickUp space creation.

    Attributes:
        name: ClickUp space name.
        space_code: ClickUp space code.
    """
    name: Optional[str] = None
    space_code: Optional[str] = None

class ClickUpSpaceRegisterDTO(BaseModel):
    """
    Payload for ClickUp space registration.

    Attributes:
        name: ClickUp space name.
        space_code: ClickUp space code.
        ignore_name: If True, skips space name validation against ClickUp.
    """
    name: Optional[str] = None
    space_code: Optional[str] = None
    ignore_name: bool = False

class ClickUpSpaceUpdateDTO(BaseModel):
    """
    Payload for ClickUp space updates.

    Attributes:
        id: ClickUp space identifier.
        name: ClickUp space name.
        space_code: ClickUp space code.
        repo: Reference to associated repository.
    """
    id: Optional[int] = None
    name: Optional[str] = None
    space_code: Optional[str] = None
    repo: Optional[ClickUpRepoRefDTO] = None

class ClickUpSpaceLightDTO(BaseModel):
    """
    ClickUp space DTO with repository summary.

    Attributes:
        id: ClickUp space identifier.
        space_code: ClickUp space code.
        name: ClickUp space name.
        repo: Associated repository details.
    """
    id: Optional[int] = None
    space_code: Optional[str] = None
    name: Optional[str] = None
    repo: Optional[ClickUpRepoDTO] = None

class ClickUpSpaceDetailDTO(BaseModel):
    """
    Detailed ClickUp space DTO with repository data.

    Attributes:
        id: ClickUp space identifier.
        name: ClickUp space name.
        space_code: ClickUp space code.
        repo: Associated repository details.
    """
    id: Optional[int] = None
    name: Optional[str] = None
    space_code: Optional[str] = None
    repo: Optional[ClickUpRepoDTO] = None