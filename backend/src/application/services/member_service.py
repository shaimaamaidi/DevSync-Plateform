import logging
from typing import List

from backend.src.domain.entities.member import MemberCreateDTO, MemberDTO, MemberUpdateDTO, MemberWithReposDTO
from backend.src.domain.entities.git_repo import GitRepoDTO
from backend.src.domain.ports.repositories.i_member_repository import IMemberRepository


logger = logging.getLogger(__name__)


class MemberService:
    def __init__(self, member_repo: IMemberRepository):
        self._repo = member_repo

    def add_member(self, member: MemberCreateDTO) -> MemberDTO:
        logger.info("Adding new member: username=%s, mail=%s", member.username, member.mail)

        result = self._repo.save(member)

        logger.info("Member added successfully: id=%s, username=%s", result.id, result.username)
        return result

    def update_member(self, member: MemberUpdateDTO) -> MemberWithReposDTO:
        logger.info("Updating member: id=%s, username=%s", member.id, member.username)

        result = self._repo.update(member)

        logger.info("Member updated successfully: id=%s, username=%s", result.id, result.username)
        return result

    def get_members_by_repo(self, repo: GitRepoDTO) -> List[MemberDTO]:
        logger.info("Fetching members for repository: repo_id=%s, repo_url=%s", repo.id, repo.url)

        results = self._repo.find_by_repo_id(repo.id)

        logger.info("Found %s members for repository successfully: repo_id=%s", len(results), repo.id)
        return results

    def get_member_by_mail(self, mail: str) -> MemberWithReposDTO:
        logger.info("Fetching member by mail: %s", mail)

        result = self._repo.find_by_mail(mail)

        logger.info("Member fetched successfully: id=%s, mail=%s", result.id, result.mail)
        return result

    def get_all_with_repos(self) -> List[MemberWithReposDTO]:
        logger.info("Fetching all members with their repositories")

        results = self._repo.find_all_with_repos()

        logger.info("Fetched %s members with repositories successfully", len(results))
        return results

    def delete(self, member_id: int) -> bool:
        logger.info("Deleting member: id=%s", member_id)

        result = self._repo.delete(member_id)

        logger.info("Member deleted successfully: id=%s", member_id)
        return result