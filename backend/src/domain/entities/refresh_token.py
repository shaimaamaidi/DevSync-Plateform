"""
Domain DTOs for refresh token data.

This module defines the DTO for managing refresh tokens used in member authentication.

Main classes:
    RefreshTokenDTO
"""

from datetime import datetime

from pydantic import BaseModel


class RefreshTokenDTO(BaseModel):
    """
    DTO for managing a refresh token.

    Attributes:
        id: Token identifier.
        member_id: Associated member identifier.
        refresh_token: Refresh token value.
        expires_at: Token expiration date.
        is_revoked: Revocation status.
    """
    id: int
    member_id: int
    refresh_token: str
    expires_at: datetime
    is_revoked: bool