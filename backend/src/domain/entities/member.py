"""
Domain DTOs for member data.

This module defines Data Transfer Objects (DTOs) for member management, used in authentication,
creation, update, and retrieval flows.

Main classes:
    MemberRole, MemberAuthDTO, MemberCredentialsDTO, MemberTokensDTO, MemberDTO, MemberCreateDTO,
    MemberUpdateDTO, MemberWithReposDTO
"""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class MemberRole(str, Enum):
    """
    Enumeration of supported member roles.

    Roles define the authorization level granted to a member
    within the platform.
    """
    ADMIN = "admin"
    MEMBER = "member"

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
        role: Member role.
        hashed_password: Hashed password.
    """
    id: int
    mail: str
    role: MemberRole
    hashed_password: str

class MemberTokensDTO(BaseModel):
    """
    Authentication response containing access and refresh tokens.

    Attributes:
        access_token: JWT access token.
        refresh_token: JWT refresh token.
        token_type: Token type (default 'bearer').
        role: Authenticated member role.
    """
    access_token: str = Field(..., description="JWT access token.")
    refresh_token: str = Field(..., description="JWT refresh token.")
    token_type: str = Field(default="bearer", description="Token type (default 'bearer').")
    role: MemberRole = Field(..., description="Authenticated member role.")

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
        role: Member role.
        mail: Email address.
    """
    id: int
    username: str
    arabic_name: str
    role: MemberRole
    mail: str

class MemberCreateDTO(BaseModel):
    """
    Payload for member creation.

    Attributes:
        username: Member username.
        arabic_name: Member Arabic name.
        mail: Member email address.
        role: Member role.
        password: Member account password.
    """
    username: str = Field(..., min_length=1, description="Member username.")
    arabic_name: str = Field(..., min_length=1, description="Member Arabic name.")
    mail: str = Field(..., min_length=1, description="Member email address.")
    role: MemberRole = Field(default=MemberRole.MEMBER, description="Member role.")
    password: str = Field(..., min_length=1, description="Member account password.")

class MemberUpdateDTO(BaseModel):
    """
    Payload for member update.

    Attributes:
        id: Member identifier.
        username: Username.
        arabic_name: Arabic name.
        role:Member role.
        mail: Email address.
        repos: List of associated repositories.
    """
    id: int
    username: Optional[str] = None
    arabic_name: Optional[str] = None
    role: Optional[MemberRole] = None
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
        role: Member role.
        repos: List of repositories (RepoSummary).
    """
    id: int
    username: str
    arabic_name: str
    mail: str
    role: Optional[MemberRole] = None
    repos: List[RepoSummary] = []