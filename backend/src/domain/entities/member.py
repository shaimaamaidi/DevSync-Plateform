"""Domain DTOs for member data."""

from typing import List, Optional

from pydantic import BaseModel, Field


class RepoSummary(BaseModel):
    """Summary view of a repository linked to a member."""
    id: Optional[int] = None
    name: Optional[str] = None
    url: Optional[str] = None

class RepoRefDTO(BaseModel):
    """Reference to a repository by id or URL."""
    id: Optional[int] = None
    url: Optional[str] = None

class MemberDTO(BaseModel):
    """Member data transfer object."""
    id: Optional[int] = None
    username: Optional[str] = None
    mail: Optional[str] = None

class MemberCreateDTO(BaseModel):
    """Payload for member creation."""
    username: Optional[str] = None
    mail: Optional[str] = None
    password: Optional[str] =None

class MemberUpdateDTO(BaseModel):
    """Payload for member updates."""
    id: Optional[int] = None
    username: Optional[str] = None
    mail: Optional[str] = None
    repos: Optional[List[RepoRefDTO]] = None

class MemberWithReposDTO(BaseModel):
    """Member DTO enriched with repositories."""
    id: Optional[int] = None
    username: Optional[str] = None
    mail: Optional[str] = None
    repos: List[RepoSummary] = Field(default_factory=list)