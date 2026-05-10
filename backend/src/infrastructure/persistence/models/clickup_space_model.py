"""
SQLAlchemy model for ClickUp spaces.

This module defines the ClickUpSpaceModel class, which represents a ClickUp space persisted in the database.

Classes:
    ClickUpSpaceModel: SQLAlchemy ORM model for ClickUp spaces.
"""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from backend.src.infrastructure.persistence.base import BaseModel


class ClickUpSpaceModel(BaseModel):
    """
    SQLAlchemy ORM model for a persisted ClickUp space record.

    Attributes:
        id (int): Primary key.
        name (str): Name of the ClickUp space.
        space_code (str): Unique code for the ClickUp space.
        repo_id (int): Foreign key referencing the associated Git repository.
        repo (GitRepoModel): Relationship to the associated Git repository.
    """
    __tablename__ = "clickup_spaces"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    space_code = Column(String(100), nullable=False, unique=True)
    repo_id = Column(Integer, ForeignKey("git_repos.id"))
    repo = relationship("GitRepoModel", back_populates="clickup_space")
