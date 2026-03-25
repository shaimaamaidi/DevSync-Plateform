from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from backend.src.infrastructure.persistence.base import Base
from backend.src.infrastructure.persistence.models.member_repo_association import member_repo_association


class MemberModel(Base):
    __tablename__ = "members"
    id = Column(Integer, primary_key=True)
    username = Column(String(255), nullable=False)
    mail = Column(String(255), nullable=False, unique=True)
    repos = relationship(
        "GitRepoModel",
        secondary=member_repo_association,
        back_populates="members",
    )