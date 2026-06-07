"""
Member service module.

This module provides the MemberService class, which manages member-related
operations such as creation, update, retrieval, and listing.
It coordinates persistence and business logic for member management.

Classes:
    MemberService: Main service for member operations.
"""

import logging
from typing import List

from backend.src.domain.entities.member import MemberCreateDTO, MemberDTO, MemberUpdateDTO, MemberWithReposDTO
from backend.src.domain.exceptions.common.invalid_input_exception import InvalidInputException
from backend.src.domain.ports.input.i_member_service import IMemberService
from backend.src.domain.ports.repositories.i_member_repository import IMemberRepository


logger = logging.getLogger(__name__)


class MemberService(IMemberService):
    """
    Application service for member operations: creation, update, retrieval, and listing.

    Coordinates persistence and business logic for member management.

    Attributes:
        _repo (IMemberRepository): Member persistence port.
    """

    def __init__(self, member_repo: IMemberRepository):
        """
        Initialize the service with a repository port.

        Args:
            member_repo (IMemberRepository): Member persistence port.
        """
        self._repo = member_repo

    def add_member(self, member: MemberCreateDTO) -> MemberDTO:
        """
        Create a new member.

        Args:
            member (MemberCreateDTO): Member create payload.

        Returns:
            MemberDTO: Created member DTO.
        """
        logger.info(
            "Adding new member: username=%s, arabic_name=%s, mail=%s.",
            member.username,
            member.arabic_name,
            member.mail
        )

        result = self._repo.save(member)

        logger.info("Member added successfully: id=%s, username=%s.", result.id, result.username)

        return result

    def update_member(self, member: MemberUpdateDTO) -> MemberWithReposDTO:
        """
        Update an existing member.

        Args:
            member (MemberUpdateDTO): Member update payload.

        Returns:
            MemberWithReposDTO: Updated member with repositories DTO.

        Raises:
            InvalidInputException: If no fields are provided for update.
        """
        logger.info("Updating member: id=%s.", member.id)

        if not any([member.username, member.arabic_name, member.mail, member.password, member.repos]):
            logger.warning("Update failed: no fields provided (id=%s).", member.id)
            raise InvalidInputException(
                "Please provide at least one field to update."
            )

        result = self._repo.update(member)

        logger.info("Member updated successfully: id=%s.", result.id)

        return result

    def get_by_id(self, member_id: int) -> MemberDTO:
        """
        Retrieve a member by their ID.

        Args:
            member_id (int): The member's database ID.

        Returns:
            MemberDTO: The member data transfer object.
        """
        logger.info("Fetching member by id=%s.", member_id)

        result = self._repo.find_by_id(member_id)

        logger.info("Member fetched successfully: id=%s, username=%s, mail=%s.", result.id, result.username,
                    result.mail)

        return result

    def get_members_by_repo(self, repo_id: int) -> List[MemberDTO]:
        """
        Fetch members associated with a repository.

        Args:
            repo_id (int): Repository ID used to resolve membership.

        Returns:
            List[MemberDTO]: List of member DTOs.
        """
        logger.info("Fetching members for repository: repo_id=%s.", repo_id)

        results = self._repo.find_by_repo_id(repo_id)

        logger.info(
            "Found %s members for repository successfully: repo_id=%s.",
            len(results),
            repo_id
        )

        return results

    def get_member_by_mail(self, mail: str) -> MemberWithReposDTO:
        """
        Fetch a member by email address.

        Args:
            mail (str): Member email.

        Returns:
            MemberWithReposDTO: Member DTO with repositories.

        Raise:
            InvalidInputException: If the MAIL is missing or invalid.
        """
        logger.info("Fetching member by mail: %s.", mail)

        if not mail:
            logger.warning(
                "Invalid input for member fetching by mail (mail=%s).",
                mail
            )
            raise InvalidInputException(
                "Please provide a valid email address."
            )

        result = self._repo.find_by_mail(mail)

        logger.info("Member fetched successfully: id=%s, mail=%s.", result.id, result.mail)

        return result

    def get_all_with_repos(self) -> List[MemberWithReposDTO]:
        """
        Return all members with their repositories.

        Returns:
            List[MemberWithReposDTO]: List of members with repositories.
        """
        logger.info("Fetching all members with their repositories.")

        results = self._repo.find_all_with_repos()

        logger.info("Fetched %s members with repositories successfully.", len(results))

        return results

    def delete(self, member_id: int) -> bool:
        """
        Delete a member by id.

        Args:
            member_id (int): Member identifier.

        Returns:
            bool: True when deletion succeeds.
        """
        logger.info("Deleting member: id=%s.", member_id)

        result = self._repo.delete(member_id)

        logger.info("Member deleted successfully: id=%s.", member_id)

        return result