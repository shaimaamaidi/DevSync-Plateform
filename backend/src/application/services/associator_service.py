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
        clickup_space.repo_id = existing_repo.id
        return self._clickup.add_space(clickup_space)

    def associate_members(self, repo: GitRepoDTO, members_data: List[dict]) -> List[MemberDTO]:
        results = []
        for m in members_data:
            missing = [f for f in ("username", "email") if f not in m]
            if missing:
                raise InvalidMemberDataException(missing_fields=missing, data=m)
            member = MemberDTO(
                username=m["username"],
                email=m["email"],
                repos=[RepoSummary(name=repo.name, url=repo.url)],
            )
            results.append(self._member.add_member(member))
        return results