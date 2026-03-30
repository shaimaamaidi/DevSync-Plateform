"""
Domain DTOs for repository association workflows.

This module defines Data Transfer Objects (DTOs) for associating repositories, members, and ClickUp spaces.

Main classes:
    MemberMailDTO, AssociateClickUpSpaceRequest, RepoMembersRequest, AssociatorRepoDTO, AssociatorMemberDTO, AssociateClickUpSpaceResponse, AssociateMembersResponse
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
    repo_url: Optional[str] = None
    space_code: Optional[str] = None

class RepoMembersRequest(BaseModel):
    """
    Request payload for associating repository members.

    Attributes:
        repo_url: Repository URL.
        members: List of member mail DTOs.
    """
    repo_url: Optional[str] = None
    members: List[MemberMailDTO] = Field(default_factory=list)

class AssociatorRepoDTO(BaseModel):
    """
    Repository summary returned in association responses.

    Attributes:
        id: Repository identifier.
        name: Repository name.
        url: Repository URL.
    """
    id: Optional[int] = None
    name: Optional[str] = None
    url: Optional[str] = None

class AssociatorMemberDTO(BaseModel):
    """
    Member summary returned in association responses.

    Attributes:
        id: Member identifier.
        name: Member name.
        mail: Member email address.
    """
    id: Optional[int] = None
    name: Optional[str] = None
    mail: Optional[str] = None


class AssociateClickUpSpaceResponse(BaseModel):
    """
    Response payload for ClickUp space association.

    Attributes:
        repo: Repository summary.
        clickup_space: Associated ClickUp space DTO.
    """
    repo: AssociatorRepoDTO
    clickup_space: Optional[ClickUpSpaceDTO] = None

class AssociateMembersResponse(BaseModel):
    """
    Response payload for member association operations.

    Attributes:
        repo: Repository summary.
        members: List of associated member DTOs.
    """
    repo: AssociatorRepoDTO
    members: List[AssociatorMemberDTO] = Field(default_factory=list)
    
    
