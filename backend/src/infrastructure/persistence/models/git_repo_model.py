"""
SQLAlchemy model for Git repositories.

This module defines the GitRepoModel class, which represents a Git repository persisted in the database.

Classes:
    GitRepoModel: SQLAlchemy ORM model for Git repositories.
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from backend.src.infrastructure.persistence.base import Base
from backend.src.infrastructure.persistence.models.member_repo_association import member_repo_association


class GitRepoModel(Base):
    """
    SQLAlchemy ORM model for a persisted Git repository record.

    Attributes:
        id (int): Primary key.
        name (str): Name of the Git repository.
        url (str): Unique URL of the repository.
        clickup_space (ClickUpSpaceModel): Relationship to the associated ClickUp space.
        members (list[MemberModel]): List of associated members.
    """
    __tablename__ = "git_repos"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    url = Column(String(255), nullable=False, unique=True)
    clickup_space = relationship("ClickUpSpaceModel", back_populates="repo", uselist=False)
    members = relationship(
        "MemberModel",
        secondary=member_repo_association,
        back_populates="repos",
    )