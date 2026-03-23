from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from backend.src.infrastructure.persistence.base import Base


class MemberModel(Base):
    __tablename__ = "members"
    id = Column(Integer, primary_key=True)
    username = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    repo_id = Column(Integer, ForeignKey("git_repos.id"), nullable=False)
    repo = relationship("GitRepoModel", back_populates="members")