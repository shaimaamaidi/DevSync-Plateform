from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class MemberSummary:
    username: str
    email: str


@dataclass
class ClickUpSpaceSummary:
    name: str


@dataclass
class GitRepoDTO:
    name: str
    url: str
    id: Optional[int] = None


@dataclass
class GitRepoDetailDTO:
    id: int
    name: str
    url: str
    members: List[MemberSummary] = field(default_factory=list)
    clickup_space: Optional[ClickUpSpaceSummary] = None