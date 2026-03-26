from typing import Optional
from pydantic import BaseModel


class ClickUpRepoDTO(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    url: Optional[str] = None


class ClickUpRepoRefDTO(BaseModel):
    id: Optional[int] = None
    url: Optional[str] = None


class ClickUpSpaceDTO(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    space_code: Optional[str] = None


class ClickUpSpaceCreateDTO(BaseModel):
    name: Optional[str] = None
    space_code: Optional[str] = None


class ClickUpSpaceUpdateDTO(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    space_code: Optional[str] = None
    repo: Optional[ClickUpRepoRefDTO] = None


class ClickUpSpaceLightDTO(BaseModel):
    id: Optional[int] = None
    space_code: Optional[str] = None
    name: Optional[str] = None
    repo: Optional[ClickUpRepoDTO] = None


class ClickUpSpaceDetailDTO(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    space_code: Optional[str] = None
    repo: Optional[ClickUpRepoDTO] = None