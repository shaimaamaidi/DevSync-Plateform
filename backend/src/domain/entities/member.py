"""
Domain DTOs for member data.

This module defines Data Transfer Objects (DTOs) for member management, used in authentication, creation, update, and retrieval flows.

Main classes:
    MemberAuthDTO, MemberCredentialsDTO, MemberTokensDTO, MemberDTO, MemberCreateDTO, MemberUpdateDTO, MemberWithReposDTO
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class MemberAuthDTO(BaseModel):
    """
    Payload for a member authentication request.

    Attributes:
        mail: Member email address.
        password: Member password.
    """
    mail: str
    password: str

class MemberCredentialsDTO(BaseModel):
    """
    Internal DTO for authentication (never exposed outside the auth flow).

    Attributes:
        id: Member identifier.
        mail: Email address.
        hashed_password: Hashed password.
    """
    id: int
    mail: str
    hashed_password: str

class MemberTokensDTO(BaseModel):
    """
    Authentication response containing access and refresh tokens.

    Attributes:
        access_token: JWT access token.
        refresh_token: JWT refresh token.
        token_type: Token type (default 'bearer').
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RepoSummary(BaseModel):
    """
    Summary view of a repository linked to a member.

    Attributes:
        id: Repository identifier.
        name: Repository name.
        url: Repository URL.
    """
    id: Optional[int] = None
    name: Optional[str] = None
    url: Optional[str] = None

class RepoRefDTO(BaseModel):
    """
    Reference to a repository by id or URL.

    Attributes:
        id: Repository identifier.
        url: Repository URL.
    """
    id: Optional[int] = None
    url: Optional[str] = None

class MemberDTO(BaseModel):
    """
    Main DTO for representing a member.

    Attributes:
        id: Member identifier.
        username: Username.
        mail: Email address.
    """
    id: Optional[int] = None
    username: Optional[str] = None
    mail: Optional[str] = None

class MemberCreateDTO(BaseModel):
    """
    Payload for member creation.

    Attributes:
        username: Username.
        mail: Email address.
        password: Password.
    """
    username: Optional[str] = None
    mail: Optional[str] = None
    password: Optional[str] =None

class MemberUpdateDTO(BaseModel):
    """
    Payload for member update.

    Attributes:
        id: Member identifier.
        username: Username.
        mail: Email address.
        repos: List of associated repositories.
    """
    id: Optional[int] = None
    username: Optional[str] = None
    mail: Optional[str] = None
    repos: Optional[List[RepoRefDTO]] = None

class MemberWithReposDTO(BaseModel):
    """
    Member DTO enriched with the list of associated repositories.

    Attributes:
        id: Member identifier.
        username: Username.
        mail: Email address.
        repos: List of repositories (RepoSummary).
    """
    id: Optional[int] = None
    username: Optional[str] = None
    mail: Optional[str] = None
    repos: List[RepoSummary] = Field(default_factory=list)