from typing import Optional
from pydantic import BaseModel


class ClickUpSpaceDTO(BaseModel):
    name: Optional[str] = None
    space_code: Optional[str] =None
    repo_id: Optional[int] = None
    id: Optional[int] = None


class ClickUpSpaceLightDTO(BaseModel):
    id: Optional[int] = None
    space_code: Optional[str] = None
    name: Optional[str] = None