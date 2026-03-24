from dataclasses import dataclass, field
from typing import List, Optional

from backend.src.domain.entities.member import RepoSummary


@dataclass
class MemberSummary:
    username: str
    email: str
    repos: List["RepoSummary"] = field(default_factory=list)

@dataclass
class ClickUpSpaceSummary:
    name: str


@dataclass
class GitRepoDTO:
    name: str
    url: str
    members: List[MemberSummary] = field(default_factory=list)
    id: Optional[int] = None


@dataclass
class GitRepoDetailDTO:
    id: int
    name: str
    url: str
    members: List[MemberSummary] = field(default_factory=list)
    clickup_space: Optional[ClickUpSpaceSummary] = None