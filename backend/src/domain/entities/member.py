from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class RepoSummary:
    name: str
    url: str


@dataclass
class MemberDTO:
    username: str
    email: str
    repos: List[RepoSummary] = field(default_factory=list)
    id: Optional[int] = None


@dataclass
class MemberWithReposDTO:
    id: int
    username: str
    email: str
    repos: List[RepoSummary] = field(default_factory=list)