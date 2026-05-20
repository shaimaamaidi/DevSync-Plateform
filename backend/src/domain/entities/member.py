"""
Domain DTOs for member data.

This module defines Data Transfer Objects (DTOs) for member management, used in authentication,
creation, update, and retrieval flows.

Main classes:
    MemberAuthDTO, MemberCredentialsDTO, MemberTokensDTO, MemberDTO, MemberCreateDTO, MemberUpdateDTO,
    MemberWithReposDTO
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
    mail: str = Field(..., min_length=1, description="Member email address used for authentication.")
    password: str = Field(..., min_length=1, description="Member account password.")

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
    access_token: str = Field(..., description="JWT access token.")
    refresh_token: str = Field(..., description="JWT refresh token.")
    token_type: str = Field(default="bearer", description="Token type (default 'bearer').")

class RepoSummary(BaseModel):
    """
    Summary view of a repository linked to a member.

    Attributes:
        id: Repository identifier.
        name: Repository name.
        url: Repository URL.
    """
    id: int
    name: str
    url: str

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
        arabic_name: Arabic name.
        mail: Email address.
    """
    id: int
    username: str
    arabic_name: str
    mail: str

class MemberCreateDTO(BaseModel):
    """
    Payload for member creation.

    Attributes:
        username: Member username.
        arabic_name: Member Arabic name.
        mail: Member email address.
        password: Member account password.
    """
    username: str = Field(..., min_length=1, description="Member username.")
    arabic_name: str = Field(..., min_length=1, description="Member Arabic name.")
    mail: str = Field(..., min_length=1, description="Member email address.")
    password: str = Field(..., min_length=1, description="Member account password.")

class MemberUpdateDTO(BaseModel):
    """
    Payload for member update.

    Attributes:
        id: Member identifier.
        username: Username.
        arabic_name: Arabic name.
        mail: Email address.
        repos: List of associated repositories.
    """
    id: int
    username: Optional[str] = None
    arabic_name: Optional[str] = None
    password: Optional[str] = None
    mail: Optional[str] = None
    repos: List[RepoRefDTO] = []

class MemberWithReposDTO(BaseModel):
    """
    Member DTO enriched with the list of associated repositories.

    Attributes:
        id: Member identifier.
        username: Username.
        arabic_name: Arabic name.
        mail: Email address.
        repos: List of repositories (RepoSummary).
    """
    id: int
    username: str
    arabic_name: str
    mail: str
    repos: List[RepoSummary] = []