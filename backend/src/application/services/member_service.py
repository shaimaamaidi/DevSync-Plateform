from typing import List

from backend.src.domain.entities.member import MemberDTO, MemberWithReposDTO
from backend.src.domain.entities.git_repo import GitRepoDTO
from backend.src.domain.exceptions.member_not_found_exception import MemberNotFoundException
from backend.src.domain.ports.repositories.i_member_repository import IMemberRepository


class MemberService:
    def __init__(self, member_repo: IMemberRepository):
        self._repo = member_repo

    def add_member(self, username: str, email: str, repo: GitRepoDTO) -> MemberDTO:
        try:
            existing = self._repo.find_by_email(email)
            existing.username = username
            existing.repo_id = repo.id
            return self._repo.save(existing)
        except MemberNotFoundException:
            return self._repo.save(MemberDTO(username=username, email=email, repo_id=repo.id))

    def get_members_by_repo(self, repo: GitRepoDTO) -> List[MemberDTO]:
        return self._repo.find_by_repo_id(repo.id)

    def get_all_with_repos(self) -> List[MemberWithReposDTO]:
        return self._repo.find_all_with_repos()

    def update(self, member_id: int, username: str = None, email: str = None) -> MemberDTO:
        dto = self._repo.find_by_id(member_id)
        if username:
            dto.username = username
        if email:
            dto.email = email
        return self._repo.save(dto)

    def delete(self, member_id: int) -> bool:
        return self._repo.delete(member_id)