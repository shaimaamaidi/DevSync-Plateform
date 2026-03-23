from dataclasses import dataclass
from typing import Optional

@dataclass
class ClickUpSpaceDTO:
    name: str
    space_id: str
    repo_id: Optional[int] = None
    id: Optional[int] = None


@dataclass
class ClickUpSpaceLightDTO:
    id: int
    space_id: str
    name: str