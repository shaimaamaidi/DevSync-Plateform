from typing import List
from src.domain.entities.git_repo import GitRepo
from src.domain.entities.member import Member
from src.domain.entities.clickup_space import ClickUpSpace
from src.application.services.clickup_service import ClickUpService
from src.application.services.member_service import MemberService


class AssociatorService:
    def __init__(self, clickup_service: ClickUpService, member_service: MemberService):
        self._clickup = clickup_service
        self._member = member_service

    def associate_space(self, repo: GitRepo, space_name: str, space_id: str) -> ClickUpSpace:
        return self._clickup.add_space(space_name, space_id, repo)

    def associate_members(self, repo: GitRepo, members_data: List[dict]) -> List[Member]:
        return [
            self._member.add_member(m["username"], m["email"], repo)
            for m in members_data
        ]