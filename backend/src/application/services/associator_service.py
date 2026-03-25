import logging
from typing import List

from backend.src.application.services.repo_service import RepoService
from backend.src.domain.entities.git_repo import GitRepoDTO
from backend.src.domain.entities.member import MemberDTO, RepoSummary
from backend.src.domain.entities.clickup_space import ClickUpSpaceDTO
from backend.src.application.services.clickup_service import ClickUpService
from backend.src.application.services.member_service import MemberService
from backend.src.domain.exceptions.invalid_member_data_exception import InvalidMemberDataException


logger = logging.getLogger(__name__)


class AssociatorService:
    def __init__(self, clickup_service: ClickUpService, member_service: MemberService, repo_service: RepoService):
        self._clickup = clickup_service
        self._member = member_service
        self._repo = repo_service

    def associate_space(self, repo: GitRepoDTO, clickup_space: ClickUpSpaceDTO) -> ClickUpSpaceDTO:
        logger.info(
            "Associating ClickUp space with repository: repo_url=%s, space_id=%s",
            repo.url,
            clickup_space.space_id,
        )

        existing_repo = self._repo.get_by_url(repo.url)
        logger.info("Repository fetched successfully: repo_id=%s", existing_repo.id)

        existing_space = self._clickup.get_by_space_id(clickup_space.space_id)
        logger.info("ClickUp space fetched successfully: space_id=%s", existing_space.id)

        existing_space.repo_id = existing_repo.id

        updated_space = self._clickup.update_space(existing_space)

        logger.info(
            "ClickUp space successfully associated with repository: repo_id=%s, space_id=%s",
            existing_repo.id,
            existing_space.id,
        )
        return updated_space

    def associate_members(self, repo: GitRepoDTO, members_data: List[dict]) -> List[MemberDTO]:
        logger.info(
            "Associating members with repository: repo_url=%s, members_count=%s",
            repo.url,
            len(members_data),
        )

        existing_repo = self._repo.get_by_url(repo.url)
        logger.info("Repository fetched successfully: repo_id=%s", existing_repo.id)

        results = []

        for m in members_data:
            logger.info("Processing member association: mail=%s", m.get("mail"))

            missing = [f for f in ("username", "mail") if f not in m]
            if missing:
                logger.warning(
                    "Invalid member data detected for repo %s: missing_fields=%s, payload=%s",
                    repo.url,
                    missing,
                    m,
                )
                raise InvalidMemberDataException(missing_fields=missing, data=m)

            existing_member = self._member.get_member_by_mail(m["mail"])
            logger.info("Member fetched successfully: member_id=%s", existing_member.id)

            updated_repos = existing_member.repos + [RepoSummary(name=existing_repo.name, url=existing_repo.url)]

            updated_member = MemberDTO(
                id=existing_member.id,
                username=existing_member.username,
                mail=existing_member.mail,
                repos=updated_repos,
            )

            updated = self._member.update_member(updated_member)

            logger.info(
                "Member successfully associated with repository: member_id=%s, repo_id=%s",
                updated.id,
                existing_repo.id,
            )
            results.append(updated)

        logger.info(
            "All members successfully associated with repository: repo_id=%s, total=%s",
            existing_repo.id,
            len(results),
        )
        return results