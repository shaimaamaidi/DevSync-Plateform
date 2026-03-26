"""Domain DTOs for Git repository data."""

from typing import List, Optional

from pydantic import BaseModel, Field


class RepoMemberDTO(BaseModel):
    """Member details inside repository responses."""
    id: Optional[int] = None
    username: Optional[str] = None
    mail: Optional[str] = None

class RepoMemberRefDTO(BaseModel):
    """Member reference by id or email."""
    id: Optional[int] = None
    mail: Optional[str] = None

class RepoClickUpSpaceDTO(BaseModel):
    """ClickUp space details associated with a repository."""
    id: Optional[int] = None
    space_code: Optional[str] = None
    name: Optional[str] = None

class RepoClickUpSpaceRefDTO(BaseModel):
    """ClickUp space reference by id or space code."""
    id: Optional[int] = None
    space_code: Optional[str] = None
    
class GitRepoDTO(BaseModel):
    """Repository DTO with minimal fields."""
    id: Optional[int] = None
    name: Optional[str] = None
    url: Optional[str] = None

class GitRepoCreateDTO(BaseModel):
    """Payload for repository creation."""
    name: Optional[str] = None
    url: Optional[str] = None
    


class GitRepoUpdateDTO(BaseModel):
    """Payload for repository updates."""
    id: Optional[int] = None
    name: Optional[str] = None
    
    url: Optional[str] = None
    members: Optional[List[RepoMemberRefDTO]] = None
    clickup_space: Optional[RepoClickUpSpaceRefDTO] = None


class GitRepoDetailDTO(BaseModel):
    """Detailed repository DTO with members and ClickUp space."""
    id: Optional[int] = None
    name: Optional[str] = None
    
    url: Optional[str] = None
    members: List[RepoMemberDTO] = Field(default_factory=list)
    clickup_space: Optional[RepoClickUpSpaceDTO] = None


class GitRepoIdDTO(BaseModel):
    """Wrapper for a repository id."""
    id: Optional[int] = None

    

class GitRepoNameDTO(BaseModel):
    """Wrapper for a repository name."""
    name: Optional[str] = None    
