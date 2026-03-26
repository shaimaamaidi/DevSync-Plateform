from abc import ABC, abstractmethod
from typing import List

from backend.src.domain.entities.member import MemberCreateDTO, MemberDTO, MemberUpdateDTO, MemberWithReposDTO


class IMemberRepository(ABC):
    @abstractmethod
    def save(self, member: MemberCreateDTO) -> MemberDTO:
        pass

    @abstractmethod
    def update(self, member: MemberUpdateDTO) -> MemberWithReposDTO:
        pass

    @abstractmethod
    def find_by_id(self, member_id: int) -> MemberDTO:
        pass

    @abstractmethod
    def find_by_mail(self, mail: str) -> MemberWithReposDTO:
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