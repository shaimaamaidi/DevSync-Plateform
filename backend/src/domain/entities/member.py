from typing import List, Optional

from pydantic import BaseModel, Field


class RepoSummary(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None


class MemberDTO(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    repos: List[RepoSummary] = Field(default_factory=list)
    id: Optional[int] = None


class MemberWithReposDTO(BaseModel):
    id: Optional[int] =  None
    username: Optional[str] = None
    email: Optional[str] = None
    repos: List[RepoSummary] = Field(default_factory=list)