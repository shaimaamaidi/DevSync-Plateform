from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from src.infrastructure.persistence.base import Base


class GitRepoModel(Base):
    __tablename__ = "git_repos"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    url = Column(String(255), nullable=False, unique=True)
    clickup_space = relationship("ClickUpSpaceModel", back_populates="repo", uselist=False)
    members = relationship("MemberModel", back_populates="repo", cascade="all, delete-orphan")
