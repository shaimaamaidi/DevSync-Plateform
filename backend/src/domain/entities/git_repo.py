from typing import List, Optional

from pydantic import BaseModel, Field

from backend.src.domain.entities.member import RepoSummary


class MemberSummary(BaseModel):
    username: Optional[str] = None
    mail: Optional[str] = None
    repos: List["RepoSummary"] = Field(default_factory=list)


class ClickUpSpaceSummary(BaseModel):
    name: Optional[str] = None
    space_code: Optional[str] = None


class GitRepoDTO(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    members: List[MemberSummary] = Field(default_factory=list)
    id: Optional[int] = None


class GitRepoDetailDTO(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    url: Optional[str] = None
    members: List[MemberSummary] = Field(default_factory=list)
    clickup_space: Optional[ClickUpSpaceSummary] = None