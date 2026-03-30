"""
Domain DTOs for Git repository data.

This module defines Data Transfer Objects (DTOs) for Git repository management, including creation, update, retrieval, and association with members and ClickUp spaces.

Main classes:
    GitRepoDTO, GitRepoCreateDTO, GitRepoUpdateDTO, GitRepoDetailDTO, GitRepoIdDTO, GitRepoNameDTO, RepoMemberDTO, RepoMemberRefDTO, RepoClickUpSpaceDTO, RepoClickUpSpaceRefDTO
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class RepoMemberDTO(BaseModel):
    """
    Member details included in repository responses.

    Attributes:
        id: Member identifier.
        username: Username.
        mail: Email address.
    """
    id: Optional[int] = None
    username: Optional[str] = None
    mail: Optional[str] = None

class RepoMemberRefDTO(BaseModel):
    """
    Reference to a member by id or email.

    Attributes:
        id: Member identifier.
        mail: Email address.
    """
    id: Optional[int] = None
    mail: Optional[str] = None

class RepoClickUpSpaceDTO(BaseModel):
    """
    ClickUp space details associated with a repository.

    Attributes:
        id: ClickUp space identifier.
        space_code: ClickUp space code.
        name: ClickUp space name.
    """
    id: Optional[int] = None
    space_code: Optional[str] = None
    name: Optional[str] = None

class RepoClickUpSpaceRefDTO(BaseModel):
    """
    Reference to a ClickUp space by id or space code.

    Attributes:
        id: ClickUp space identifier.
        space_code: ClickUp space code.
    """
    id: Optional[int] = None
    space_code: Optional[str] = None
    
class GitRepoDTO(BaseModel):
    """
    Repository DTO with minimal fields.

    Attributes:
        id: Repository identifier.
        name: Repository name.
        url: Repository URL.
    """
    id: Optional[int] = None
    name: Optional[str] = None
    url: Optional[str] = None

class GitRepoCreateDTO(BaseModel):
    """
    Payload for repository creation.

    Attributes:
        name: Repository name.
        url: Repository URL.
    """
    name: Optional[str] = None
    url: Optional[str] = None

class GitRepoUpdateDTO(BaseModel):
    """
    Payload for repository updates.

    Attributes:
        id: Repository identifier.
        name: Repository name.
        url: Repository URL.
        members: List of member references.
        clickup_space: Reference to associated ClickUp space.
    """
    id: Optional[int] = None
    name: Optional[str] = None
    url: Optional[str] = None
    members: Optional[List[RepoMemberRefDTO]] = None
    clickup_space: Optional[RepoClickUpSpaceRefDTO] = None


class GitRepoDetailDTO(BaseModel):
    """
    Detailed repository DTO with members and ClickUp space.

    Attributes:
        id: Repository identifier.
        name: Repository name.
        url: Repository URL.
        members: List of member details.
        clickup_space: Associated ClickUp space details.
    """
    id: Optional[int] = None
    name: Optional[str] = None
    url: Optional[str] = None
    members: List[RepoMemberDTO] = Field(default_factory=list)
    clickup_space: Optional[RepoClickUpSpaceDTO] = None


class GitRepoIdDTO(BaseModel):
    """
    Wrapper for a repository id.

    Attributes:
        id: Repository identifier.
    """
    id: Optional[int] = None

class GitRepoNameDTO(BaseModel):
    """
    Wrapper for a repository name.

    Attributes:
        name: Repository name.
    """
    name: Optional[str] = None    
