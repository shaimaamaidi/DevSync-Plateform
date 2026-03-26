from typing import List, Optional

from pydantic import BaseModel, Field


class RepoSummary(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    url: Optional[str] = None


class RepoRefDTO(BaseModel):
    id: Optional[int] = None
    url: Optional[str] = None


class MemberDTO(BaseModel):
    id: Optional[int] = None
    username: Optional[str] = None
    mail: Optional[str] = None


class MemberCreateDTO(BaseModel):
    username: Optional[str] = None
    mail: Optional[str] = None


class MemberUpdateDTO(BaseModel):
    id: Optional[int] = None
    username: Optional[str] = None
    mail: Optional[str] = None
    repos: Optional[List[RepoRefDTO]] = None


class MemberWithReposDTO(BaseModel):
    id: Optional[int] = None
    username: Optional[str] = None
    mail: Optional[str] = None
    repos: List[RepoSummary] = Field(default_factory=list)