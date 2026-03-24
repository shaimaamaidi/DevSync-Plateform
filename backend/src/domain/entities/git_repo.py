from typing import List, Optional

from pydantic import BaseModel

from backend.src.domain.entities.member import RepoSummary


class MemberSummary(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    repos: List["RepoSummary"] = []


class ClickUpSpaceSummary(BaseModel):
    name: Optional[str] = None
    space_id: Optional[str] = None


class GitRepoDTO(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    members: List[MemberSummary] = []
    id: Optional[int] = None


class GitRepoDetailDTO(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    url: Optional[str] = None
    members: List[MemberSummary] =[]
    clickup_space: Optional[ClickUpSpaceSummary] = None