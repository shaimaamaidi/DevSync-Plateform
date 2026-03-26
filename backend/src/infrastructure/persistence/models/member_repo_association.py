"""Association table between members and repositories."""

from sqlalchemy import Table, Column, Integer, ForeignKey
from backend.src.infrastructure.persistence.base import Base

member_repo_association = Table(
    "member_repo",
    Base.metadata,
    Column("member_id", Integer, ForeignKey("members.id"), primary_key=True),
    Column("repo_id", Integer, ForeignKey("git_repos.id"), primary_key=True),
)