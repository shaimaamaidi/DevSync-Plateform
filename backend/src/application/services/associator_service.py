from typing import List

from backend.src.application.services.repo_service import RepoService
from backend.src.domain.entities.git_repo import GitRepoDTO
from backend.src.domain.entities.member import MemberDTO, RepoSummary
from backend.src.domain.entities.clickup_space import ClickUpSpaceDTO
from backend.src.application.services.clickup_service import ClickUpService
from backend.src.application.services.member_service import MemberService
from backend.src.domain.exceptions.invalid_member_data_exception import InvalidMemberDataException


class AssociatorService:
    def __init__(self, clickup_service: ClickUpService, member_service: MemberService, repo_service: RepoService):
        self._clickup = clickup_service
        self._member = member_service
        self._repo = repo_service

    def associate_space(self, repo: GitRepoDTO, clickup_space: ClickUpSpaceDTO) -> ClickUpSpaceDTO:
        existing_repo = self._repo.get_by_url(repo.url)
        existing_space = self._clickup.get_by_space_id(clickup_space.space_id)
        existing_space.repo_id = existing_repo.id
        return self._clickup.update_space(existing_space)

    def associate_members(self, repo: GitRepoDTO, members_data: List[dict]) -> List[MemberDTO]:
        existing_repo = self._repo.get_by_url(repo.url)
        results = []
        for m in members_data:
            missing = [f for f in ("username", "email") if f not in m]
            if missing:
                raise InvalidMemberDataException(missing_fields=missing, data=m)

            existing_member = self._member.get_member_by_email(m["email"])
            updated_repos = existing_member.repos + [RepoSummary(name=existing_repo.name, url=existing_repo.url)]
            updated_member = MemberDTO(
                id=existing_member.id,
                username=existing_member.username,
                email=existing_member.email,
                repos=updated_repos,
            )
            results.append(self._member.update_member(updated_member))

        return results