"""SQLAlchemy model for Git repositories."""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from backend.src.infrastructure.persistence.base import Base
from backend.src.infrastructure.persistence.models.member_repo_association import member_repo_association


class GitRepoModel(Base):
    """Persisted Git repository record."""
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