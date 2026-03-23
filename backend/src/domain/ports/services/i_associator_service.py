from abc import ABC, abstractmethod
from typing import List
from backend.src.domain.entities.git_repo import GitRepoDTO
from backend.src.domain.entities.member import MemberDTO
from backend.src.domain.entities.clickup_space import ClickUpSpaceDTO


class IAssociatorService(ABC):
    @abstractmethod
    def associate_space(self, repo: GitRepoDTO, space_name: str, space_id: str) -> ClickUpSpaceDTO:
        pass

    @abstractmethod
    def associate_members(self, repo: GitRepoDTO, members_data: List[dict]) -> List[MemberDTO]:
        pass