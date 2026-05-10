"""
SQLAlchemy model for refresh tokens.

This module defines the RefreshTokenModel class, which represents a refresh token persisted in the database for a member.

Classes:
    RefreshTokenModel: SQLAlchemy ORM model for refresh tokens.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from backend.src.infrastructure.persistence.base import BaseModel


class RefreshTokenModel(BaseModel):
    """
    SQLAlchemy ORM model for a persisted refresh token for members.

    Attributes:
        id (int): Primary key.
        member_id (int): Foreign key referencing the associated member.
        refresh_token (str): The refresh token string (unique).
        expires_at (datetime): Expiration datetime of the token.
        is_revoked (bool): Whether the token is revoked.
        created_at (datetime): Creation timestamp.
        member (MemberModel): Relationship to the associated member.
    """
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)

    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)

    refresh_token = Column(String(500), nullable=False, unique=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_revoked = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    member = relationship("MemberModel", back_populates="refresh_tokens")