from typing import List, Optional

from pydantic import BaseModel, Field


class RepoMemberDTO(BaseModel):
    id: Optional[int] = None
    username: Optional[str] = None
    mail: Optional[str] = None


class RepoMemberRefDTO(BaseModel):
    id: Optional[int] = None
    mail: Optional[str] = None


class RepoClickUpSpaceDTO(BaseModel):
    id: Optional[int] = None
    space_code: Optional[str] = None
    name: Optional[str] = None


class RepoClickUpSpaceRefDTO(BaseModel):
    id: Optional[int] = None
    space_code: Optional[str] = None


class GitRepoDTO(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    url: Optional[str] = None


class GitRepoCreateDTO(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None


class GitRepoUpdateDTO(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    url: Optional[str] = None
    members: Optional[List[RepoMemberRefDTO]] = None
    clickup_space: Optional[RepoClickUpSpaceRefDTO] = None


class GitRepoDetailDTO(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    url: Optional[str] = None
    members: List[RepoMemberDTO] = Field(default_factory=list)
    clickup_space: Optional[RepoClickUpSpaceDTO] = None


class GitRepoIdDTO(BaseModel):
    id: Optional[int] = None


class GitRepoNameDTO(BaseModel):
    name: Optional[str] = None