"""
Domain DTOs for repository association workflows.

This module defines Data Transfer Objects (DTOs) for associating repositories, members, and ClickUp spaces.

Main classes:
    MemberMailDTO, AssociateClickUpSpaceRequest, RepoMembersRequest, AssociatorRepoDTO,
    AssociatorMemberDTO, AssociateClickUpSpaceResponse, AssociateMembersResponse
"""

from typing import List, Optional

from pydantic import BaseModel, Field

from backend.src.domain.entities.clickup_space import ClickUpSpaceDTO


class MemberMailDTO(BaseModel):
    """
    Minimal member payload containing email address.

    Attributes:
        mail: Member email address.
    """
    mail: Optional[str] = None

class AssociateClickUpSpaceRequest(BaseModel):
    """
    Request payload for associating a ClickUp space.

    Attributes:
        repo_url: Repository URL.
        space_code: ClickUp space code.
    """
    repo_url: str = Field(..., min_length=1, description="Repository URL")
    space_code: str = Field(..., min_length=1, description="ClickUp space code")

class RepoMembersRequest(BaseModel):
    """
    Request payload for associating repository members.

    Attributes:
        repo_url: Repository URL.
        members: List of member mail DTOs.
    """
    repo_url: str = Field(..., min_length=1, description="Repository URL")
    members: List[MemberMailDTO] = []

class AssociatorRepoDTO(BaseModel):
    """
    Repository summary returned in association responses.

    Attributes:
        id: Repository identifier.
        name: Repository name.
        url: Repository URL.
    """
    id: int
    name: str
    url: str

class AssociatorMemberDTO(BaseModel):
    """
    Member summary returned in association responses.

    Attributes:
        id: Member identifier.
        username: Member name.
        arabic_name: Arabic name.
        mail: Member email address.
    """
    id: int
    username: str
    arabic_name: str
    mail: str


class AssociateClickUpSpaceResponse(BaseModel):
    """
    Response payload for ClickUp space association.

    Attributes:
        repo: Repository summary.
        clickup_space: Associated ClickUp space DTO.
    """
    repo: AssociatorRepoDTO
    clickup_space: ClickUpSpaceDTO

class AssociateMembersResponse(BaseModel):
    """
    Response payload for member association operations.

    Attributes:
        repo: Repository summary.
        members: List of associated member DTOs.
    """
    repo: AssociatorRepoDTO
    members: List[AssociatorMemberDTO] = []
    
    
