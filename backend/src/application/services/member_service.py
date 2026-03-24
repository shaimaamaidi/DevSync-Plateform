from typing import List

from backend.src.domain.entities.member import MemberDTO, MemberWithReposDTO
from backend.src.domain.entities.git_repo import GitRepoDTO
from backend.src.domain.ports.repositories.i_member_repository import IMemberRepository


class MemberService:
    def __init__(self, member_repo: IMemberRepository):
        self._repo = member_repo

    def add_member(self, member: MemberDTO) -> MemberDTO:
        return self._repo.save(member)

    def update_member(self, member: MemberDTO) -> MemberDTO:
        return self._repo.update(member)

    def get_members_by_repo(self, repo: GitRepoDTO) -> List[MemberDTO]:
        return self._repo.find_by_repo_id(repo.id)

    def get_member_by_email(self, repo: GitRepoDTO) -> MemberDTO:
        return self._repo.find_by_email(repo.email)

    def get_all_with_repos(self) -> List[MemberWithReposDTO]:
        return self._repo.find_all_with_repos()

    def delete(self, member_id: int) -> bool:
        return self._repo.delete(member_id)