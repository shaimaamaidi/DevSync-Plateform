from typing import List, Optional

from pydantic import BaseModel, Field

from backend.src.domain.entities.clickup_space import ClickUpSpaceDTO


class MemberMailDTO(BaseModel):
    mail: Optional[str] = None


class AssociateClickUpSpaceRequest(BaseModel):
    repo_url: Optional[str] = None
    space_code: Optional[str] = None


class RepoMembersRequest(BaseModel):
    repo_url: Optional[str] = None
    members: List[MemberMailDTO] = Field(default_factory=list)


class AssociatorRepoDTO(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    url: Optional[str] = None


class AssociatorMemberDTO(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    mail: Optional[str] = None


class AssociateClickUpSpaceResponse(BaseModel):
    repo: AssociatorRepoDTO
    clickup_space: Optional[ClickUpSpaceDTO] = None


class AssociateMembersResponse(BaseModel):
    repo: AssociatorRepoDTO
    members: List[AssociatorMemberDTO] = Field(default_factory=list)
