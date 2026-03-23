from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from src.infrastructure.persistence.base import Base


class ClickUpSpaceModel(Base):
    __tablename__ = "clickup_spaces"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    space_id = Column(String(100), nullable=False, unique=True)
    repo_id = Column(Integer, ForeignKey("git_repos.id"))
    repo = relationship("GitRepoModel", back_populates="clickup_space")
