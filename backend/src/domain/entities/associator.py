"""Domain DTOs for repository association workflows."""

from typing import List, Optional

from pydantic import BaseModel, Field

from backend.src.domain.entities.clickup_space import ClickUpSpaceDTO


class MemberMailDTO(BaseModel):
    """Minimal member payload containing email address."""
    mail: Optional[str] = None

class AssociateClickUpSpaceRequest(BaseModel):
    """Request payload for associating a ClickUp space."""
    repo_url: Optional[str] = None
    space_code: Optional[str] = None

class RepoMembersRequest(BaseModel):
    """Request payload for associating repository members."""
    repo_url: Optional[str] = None
    members: List[MemberMailDTO] = Field(default_factory=list)

class AssociatorRepoDTO(BaseModel):
    """Repository summary returned in association responses."""
    id: Optional[int] = None
    name: Optional[str] = None
    url: Optional[str] = None

class AssociatorMemberDTO(BaseModel):
    """Member summary returned in association responses."""
    id: Optional[int] = None
    name: Optional[str] = None
    
    
    mail: Optional[str] = None


class AssociateClickUpSpaceResponse(BaseModel):
    """Response payload for ClickUp space association."""
    repo: AssociatorRepoDTO
    clickup_space: Optional[ClickUpSpaceDTO] = None

class AssociateMembersResponse(BaseModel):
    """Response payload for member association operations."""
    repo: AssociatorRepoDTO
    members: List[AssociatorMemberDTO] = Field(default_factory=list)
    
    
