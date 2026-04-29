"""
Associator use case module.

This module provides the AssociatorUseCase class, which manages associations between repositories, ClickUp spaces, and members.
It coordinates the logic for linking repositories to ClickUp spaces and members, and delegates persistence and business logic to the appropriate services.

Classes:
    AssociatorUseCase: Main use case for managing repository associations with ClickUp and members.
"""

import logging

from backend.src.domain.entities.associator import (
    AssociateClickUpSpaceRequest,
    AssociateClickUpSpaceResponse,
    AssociateMembersResponse,
    AssociatorMemberDTO,
    AssociatorRepoDTO,
    RepoMembersRequest,
)
from backend.src.domain.entities.git_repo import GitRepoUpdateDTO, RepoClickUpSpaceRefDTO, RepoMemberRefDTO
from backend.src.domain.exceptions.member.invalid_member_data_exception import InvalidMemberDataException
from backend.src.domain.ports.input.i_associator_use_case import IAssociatorUseCase
from backend.src.domain.ports.repositories.i_clickup_repository import IClickUpRepository
from backend.src.domain.ports.repositories.i_member_repository import IMemberRepository
from backend.src.domain.ports.repositories.i_repo_repository import IRepoRepository

logger = logging.getLogger(__name__)


class AssociatorUseCase(IAssociatorUseCase):
    """
    Application use case for managing associations between repositories, ClickUp spaces, and members.

    Coordinates the logic for linking repositories to ClickUp spaces and members, delegating persistence and business logic to the appropriate services.

    Attributes:
        _repo (IRepoRepository): Repository application service.
        _clickup (IClickUpRepository): ClickUp application service.
        _member (IMemberRepository): Member application service.
    """

    def __init__(self, repo_service: IRepoRepository, clickup_service: IClickUpRepository,
                 member_service: IMemberRepository):
        """
        Initialize the use case with dependent services.

        Args:
            repo_service (IRepoRepository): Repository persistence port.
            clickup_service (IClickUpRepository): Click Up persistence port.
            member_service (IMemberRepository): Member persistence port.
        """
        self._repo = repo_service
        self._clickup = clickup_service
        self._member = member_service

    def associate_clickup_space(self, request: AssociateClickUpSpaceRequest) -> AssociateClickUpSpaceResponse:
        """
        Associate a ClickUp space with a repository.

        Args:
            request (AssociateClickUpSpaceRequest): Association request payload.

        Returns:
            AssociateClickUpSpaceResponse: ClickUp space association response.
        """
        logger.info(
            "Associating ClickUp space with repository: repo_url=%s, space_code=%s.",
            request.repo_url,
            request.space_code,
        )

        clickup_space = self._clickup.find_by_space_code(request.space_code)
        existing_repo = self._repo.find_by_url(request.repo_url)

        logger.info("Repository fetched successfully: repo_id=%s.", existing_repo.id)

        update_payload = GitRepoUpdateDTO(
            id=existing_repo.id,
            clickup_space=RepoClickUpSpaceRefDTO(space_code=clickup_space.space_code),
        )

        updated_repo = self._repo.update(update_payload)

        logger.info(
            "Association completed successfully: repo_id=%s, space_code=%s.",
            updated_repo.id,
            clickup_space.space_code,
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

    def add_members(self, request: RepoMembersRequest) -> AssociateMembersResponse:
        """
        Add members to a repository.

        Args:
            request (RepoMembersRequest): Repository members request.

        Returns:
            AssociateMembersResponse: Members association response.

        Raises:
            InvalidMemberDataException: If a member is missing required fields.
        """
        logger.info(
            "Adding members to repository: repo_url=%s, members_count=%s.",

            request.repo_url,
            len(request.members),
        )

        existing_repo = self._repo.find_by_url(request.repo_url)
        repo_detail = self._repo.find_by_id(existing_repo.id)

        existing_mails = {m.mail for m in repo_detail.members if m.mail}
        incoming_mails = []

        for member in request.members:
            if not member.mail:
                logger.warning(
                    "Invalid member data: missing mail in repo_url=%s.",
                    request.repo_url,
                )
                raise InvalidMemberDataException(missing_fields=["mail"], data=member.model_dump())

            existing_member = self._member.find_by_mail(member.mail)
            incoming_mails.append(existing_member.mail)

        merged_mails = existing_mails.union(incoming_mails)
        update_payload = GitRepoUpdateDTO(
            id=existing_repo.id,
            members=[RepoMemberRefDTO(mail=mail) for mail in merged_mails],
        )

        updated_repo = self._repo.update(update_payload)

        logger.info(
            "Members added successfully to repo_id=%s. Total members=%s.",
            existing_repo.id,
            len(updated_repo.members),
        )

        return self._build_members_response(updated_repo)

    def remove_members(self, request: RepoMembersRequest) -> AssociateMembersResponse:
        """
        Remove members from a repository.

        Args:
            request (RepoMembersRequest): Repository members request.

        Returns:
            AssociateMembersResponse: Members association response.

        Raises:
            InvalidMemberDataException: If a member is missing required fields.
        """
        logger.info(
            "Removing members from repository: repo_url=%s, members_count=%s.",
            request.repo_url,
            len(request.members),
        )

        existing_repo = self._repo.find_by_url(request.repo_url)
        repo_detail = self._repo.find_by_id(existing_repo.id)

        existing_mails = {m.mail for m in repo_detail.members if m.mail}
        remove_mails = set()

        for member in request.members:
            if not member.mail:
                logger.warning(
                    "Invalid member data: missing mail in repo_url=%s.",
                    request.repo_url,
                )
                raise InvalidMemberDataException(missing_fields=["mail"], data=member.model_dump())

            existing_member = self._member.find_by_mail(member.mail)
            remove_mails.add(existing_member.mail)

        remaining_mails = existing_mails - remove_mails
        update_payload = GitRepoUpdateDTO(
            id=existing_repo.id,
            members=[RepoMemberRefDTO(mail=mail) for mail in remaining_mails],
        )

        updated_repo = self._repo.update(update_payload)

        logger.info(
            "Members removed successfully from repo_id=%s. Remaining members=%s.",
            existing_repo.id,
            len(updated_repo.members),
        )

        return AssociatorUseCase._build_members_response(updated_repo)

    def update_members(self, request: RepoMembersRequest) -> AssociateMembersResponse:
        """
        Replace repository members with the provided list.

        Args:
            request (RepoMembersRequest): Repository members request.

        Returns:
            AssociateMembersResponse: Members association response.

        Raises:
            InvalidMemberDataException: If a member is missing required fields.
        """
        logger.info(
            "Updating repository members list: repo_url=%s, members_count=%s.",
            request.repo_url,
            len(request.members),
        )

        existing_repo = self._repo.find_by_url(request.repo_url)
        update_mails = []

        for member in request.members:
            if not member.mail:
                logger.warning(
                    "Invalid member data: missing mail in repo_url=%s.",
                    request.repo_url,
                )
                raise InvalidMemberDataException(missing_fields=["mail"], data=member.model_dump())

            existing_member = self._member.find_by_mail(member.mail)
            update_mails.append(existing_member.mail)

        update_payload = GitRepoUpdateDTO(
            id=existing_repo.id,
            members=[RepoMemberRefDTO(mail=mail) for mail in update_mails],
        )

        updated_repo = self._repo.update(update_payload)

        logger.info(
            "Members updated successfully for repo_id=%s. New members count=%s.",
            existing_repo.id,
            len(updated_repo.members),
        )

        return self._build_members_response(updated_repo)

    @staticmethod
    def _build_members_response(updated_repo) -> AssociateMembersResponse:
        """
        Build a members association response from a repo detail.

        Args:
            updated_repo (GitRepoDetailDTO): Repository detail DTO.

        Returns:
            AssociateMembersResponse: Members association response DTO.
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