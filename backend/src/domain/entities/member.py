from typing import List, Optional

from pydantic import BaseModel


class RepoSummary(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None


class MemberDTO(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    repos: List[RepoSummary] = []
    id: Optional[int] = None


class MemberWithReposDTO(BaseModel):
    id: Optional[int] =  None
    username: Optional[str] = None
    email: Optional[str] = None
    repos: List[RepoSummary] = []