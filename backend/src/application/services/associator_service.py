"""Application service for repository associations."""

import logging

from backend.src.application.services.clickup_service import ClickUpService
from backend.src.application.services.member_service import MemberService
from backend.src.application.services.repo_service import RepoService
from backend.src.domain.entities.associator import (
    AssociateClickUpSpaceRequest,
    AssociateClickUpSpaceResponse,
    AssociateMembersResponse,
    AssociatorMemberDTO,
    AssociatorRepoDTO,
    RepoMembersRequest,
)
from backend.src.domain.entities.git_repo import GitRepoIdDTO, GitRepoUpdateDTO, RepoClickUpSpaceRefDTO, RepoMemberRefDTO
from backend.src.domain.exceptions.invalid_member_data_exception import InvalidMemberDataException


logger = logging.getLogger(__name__)


class AssociatorService:
    """Associate repositories with ClickUp spaces and members."""
    def __init__(self, repo_service: RepoService, clickup_service: ClickUpService, member_service:MemberService):
        """Initialize the service with dependent services.

        Args:
            repo_service: Repository application service.
            clickup_service: ClickUp application service.
            member_service: Member application service.
        """
        self._repo = repo_service
        self._clickup = clickup_service
        self._member = member_service

    def associate_clickup_space(self, request: AssociateClickUpSpaceRequest):
        """Associate a ClickUp space with a repository.

        Args:
            request: Association request payload.

        Returns:
            ClickUp space association response.
        """
        logger.info(
            "Associating ClickUp space with repository: repo_url=%s, space_code=%s.",
            request.repo_url,
            request.space_code,
        )

        clickup_space = self._clickup.get_by_space_code(request.space_code)
        existing_repo = self._repo.get_by_url(request.repo_url)
        logger.info("Repository fetched successfully: repo_id=%s.", existing_repo.id)

        update_payload = GitRepoUpdateDTO(
            id=existing_repo.id,
            clickup_space=RepoClickUpSpaceRefDTO(space_code=clickup_space.space_code),
        )

        updated_repo = self._repo.update_repo(update_payload)

        logger.info(
            "ClickUp space successfully associated with repository: repo_id=%s.",
            existing_repo.id,
        )
        repo_dto = AssociatorRepoDTO(
            id=updated_repo.id,
            name=updated_repo.name,
            url=updated_repo.url,
        )
        return AssociateClickUpSpaceResponse(
            repo=repo_dto,
            clickup_space=clickup_space,
        )

    def add_members(self, request: RepoMembersRequest):
        """Add members to a repository.

        Args:
            request: Repository members request.

        Returns:
            Members association response.
        """
        logger.info(
            "Adding members to repository: repo_url=%s, members_count=%s.",
        
            request.repo_url,
            len(request.members),
        )

        existing_repo = self._repo.get_by_url(request.repo_url)
        repo_detail = self._repo.get_by_id(GitRepoIdDTO(id=existing_repo.id))

        existing_mails = {m.mail for m in repo_detail.members if m.mail}
        incoming_mails = []

        for member in request.members:
            if not member.mail:
                raise InvalidMemberDataException(missing_fields=["mail"], data=member.model_dump())
            existing_member = self._member.get_member_by_mail(member.mail)
            incoming_mails.append(existing_member.mail)

        merged_mails = existing_mails.union(incoming_mails)
        update_payload = GitRepoUpdateDTO(
            id=existing_repo.id,
            members=[RepoMemberRefDTO(mail=mail) for mail in merged_mails],
        )

        updated_repo = self._repo.update_repo(update_payload)
        return self._build_members_response(updated_repo)

    def remove_members(self, request: RepoMembersRequest):
        """Remove members from a repository.

        Args:
            request: Repository members request.

        Returns:
            Members association response.
        """
        logger.info(
            "Removing members from repository: repo_url=%s, members_count=%s.",
            request.repo_url,
            len(request.members),
        )

        existing_repo = self._repo.get_by_url(request.repo_url)
        repo_detail = self._repo.get_by_id(GitRepoIdDTO(id=existing_repo.id))

        existing_mails = {m.mail for m in repo_detail.members if m.mail}
        remove_mails = set()

        for member in request.members:
            if not member.mail:
                raise InvalidMemberDataException(missing_fields=["mail"], data=member.model_dump())
            existing_member = self._member.get_member_by_mail(member.mail)
            remove_mails.add(existing_member.mail)

        remaining_mails = existing_mails - remove_mails
        update_payload = GitRepoUpdateDTO(
            id=existing_repo.id,
            members=[RepoMemberRefDTO(mail=mail) for mail in remaining_mails],
        )

        updated_repo = self._repo.update_repo(update_payload)
        return AssociatorService._build_members_response(updated_repo)

    @staticmethod
    def _build_members_response(updated_repo):
        """Build a members association response from a repo detail.

        Args:
            updated_repo: Repository detail DTO.

        Returns:
            Members association response DTO.
        """
        repo_dto = AssociatorRepoDTO(
            id=updated_repo.id,
        
            name=updated_repo.name,
            url=updated_repo.url,
        )
        members = [
            AssociatorMemberDTO(
                id=member.id,
                name=member.username,
                mail=member.mail,
            )
            for member in updated_repo.members
        ]
        return AssociateMembersResponse(repo=repo_dto, members=members)

    def update_members(self, request: RepoMembersRequest):
        """Replace repository members with the provided list.

        Args:
            request: Repository members request.

        Returns:
            Members association response.
        """
        logger.info(
            "Updating repository members list: repo_url=%s, members_count=%s.",
            request.repo_url,
            len(request.members),
        )

        existing_repo = self._repo.get_by_url(request.repo_url)
        update_mails = []

        for member in request.members:
            if not member.mail:
                raise InvalidMemberDataException(missing_fields=["mail"], data=member.model_dump())
            existing_member = self._member.get_member_by_mail(member.mail)
            update_mails.append(existing_member.mail)

        update_payload = GitRepoUpdateDTO(
            id=existing_repo.id,
            members=[RepoMemberRefDTO(mail=mail) for mail in update_mails],
        )

        updated_repo = self._repo.update_repo(update_payload)
        return self._build_members_response(updated_repo)