from abc import ABC, abstractmethod
from typing import List

from backend.src.domain.entities.member import MemberDTO, MemberWithReposDTO


class IMemberRepository(ABC):
    @abstractmethod
    def save(self, member: MemberDTO) -> MemberDTO:
        pass

    @abstractmethod
    def update(self, member: MemberDTO) -> MemberDTO:
        pass

    @abstractmethod
    def find_by_id(self, member_id: int) -> MemberDTO:
        pass

    @abstractmethod
    def find_by_mail(self, mail: str) -> MemberDTO:
        pass

    @abstractmethod
    def find_by_repo_id(self, repo_id: int) -> List[MemberDTO]:
        pass

    @abstractmethod
    def find_all_with_repos(self) -> List[MemberWithReposDTO]:
        pass

    @abstractmethod
    def delete(self, member_id: int) -> bool:
        pass