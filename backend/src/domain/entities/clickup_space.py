"""Domain DTOs for ClickUp space data."""

from typing import Optional
from pydantic import BaseModel


class ClickUpRepoDTO(BaseModel):
    """Repository details embedded in ClickUp space responses."""
    id: Optional[int] = None
    name: Optional[str] = None
    url: Optional[str] = None

class ClickUpRepoRefDTO(BaseModel):
    """Reference to a repository linked to a ClickUp space."""
    id: Optional[int] = None
    url: Optional[str] = None

class ClickUpSpaceDTO(BaseModel):
    """ClickUp space DTO with minimal fields."""
    id: Optional[int] = None
    name: Optional[str] = None
    space_code: Optional[str] = None


class ClickUpSpaceCreateDTO(BaseModel):
    """Payload for ClickUp space creation."""
    name: Optional[str] = None
    space_code: Optional[str] = None

class ClickUpSpaceUpdateDTO(BaseModel):
    """Payload for ClickUp space updates."""
    id: Optional[int] = None
    name: Optional[str] = None
    space_code: Optional[str] = None
    repo: Optional[ClickUpRepoRefDTO] = None

class ClickUpSpaceLightDTO(BaseModel):
    """ClickUp space DTO with repo summary."""
    id: Optional[int] = None
    space_code: Optional[str] = None
    name: Optional[str] = None
    repo: Optional[ClickUpRepoDTO] = None

class ClickUpSpaceDetailDTO(BaseModel):
    """Detailed ClickUp space DTO with repository data."""
    id: Optional[int] = None
    name: Optional[str] = None
    space_code: Optional[str] = None
    repo: Optional[ClickUpRepoDTO] = None