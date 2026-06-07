"""
SQLAlchemy model for members.

This module defines the MemberModel class, which represents a member persisted in the database.

Classes:
    MemberModel: SQLAlchemy ORM model for members.
"""

from sqlalchemy import Column, Integer, String, Enum as SAEnum
from sqlalchemy.orm import relationship

from backend.src.domain.entities.member import MemberRole
from backend.src.infrastructure.persistence.base import BaseModel
from backend.src.infrastructure.persistence.models.member_repo_association import member_repo_association


class MemberModel(BaseModel):
    """
    SQLAlchemy ORM model for a persisted member record.

    Attributes:
        id (int): Primary key.
        username (str): Username of the member.
        arabic_name (str): Arabic name of the member.
        mail (str): Unique email address of the member.
        password (str): Hashed password of the member.
        repos (list[GitRepoModel]): List of associated Git repositories.
        refresh_tokens (list[RefreshTokenModel]): List of associated refresh tokens.
    """
    __tablename__ = "members"

    id = Column(Integer, primary_key=True)
    username = Column(String(255), nullable=False)
    arabic_name = Column(String(255), nullable=False)
    mail = Column(String(255), nullable=False, unique=True)
    role = Column(
        SAEnum(MemberRole, name="member_role_enum"),
        nullable=False,
        default=MemberRole.MEMBER,
    )
    password = Column(String(255), nullable=False)

    repos = relationship(
        "GitRepoModel",
        secondary=member_repo_association,
        back_populates="members",
    )

    refresh_tokens = relationship(
        "RefreshTokenModel",
        back_populates="member",
        cascade="all, delete-orphan"
    )