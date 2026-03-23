from typing import List
from backend.src.domain.entities.git_repo import GitRepoDTO
from backend.src.domain.entities.member import MemberDTO
from backend.src.domain.entities.clickup_space import ClickUpSpaceDTO
from backend.src.application.services.clickup_service import ClickUpService
from backend.src.application.services.member_service import MemberService


class AssociatorService:
    def __init__(self, clickup_service: ClickUpService, member_service: MemberService):
        self._clickup = clickup_service
        self._member = member_service

    def associate_space(self, repo: GitRepoDTO, space_name: str, space_id: str) -> ClickUpSpaceDTO:
        return self._clickup.add_space(space_name, space_id, repo)

    def associate_members(self, repo: GitRepoDTO, members_data: List[dict]) -> List[MemberDTO]:
        return [
            self._member.add_member(m["username"], m["email"], repo)
            for m in members_data
        ]