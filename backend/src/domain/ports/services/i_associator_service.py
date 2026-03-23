from abc import ABC, abstractmethod
from typing import List
from src.domain.entities.git_repo import GitRepo
from src.domain.entities.member import Member
from src.domain.entities.clickup_space import ClickUpSpace


class IAssociatorService(ABC):
    @abstractmethod
    def associate_space(self, repo: GitRepo, space_name: str, space_id: str) -> ClickUpSpace:
        pass

    @abstractmethod
    def associate_members(self, repo: GitRepo, members_data: List[dict]) -> List[Member]:
        pass