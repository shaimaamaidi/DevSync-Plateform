"""
Service port for member management operations.

This module defines the IMemberService interface, which specifies operations
for managing application members such as creation, update, retrieval, and deletion.

It acts as a contract for application-level services responsible for:
- Creating and updating members
- Retrieving members by different criteria (email, repository)
- Listing members with their associated repositories
- Deleting members
"""

from abc import ABC, abstractmethod
from typing import List

from backend.src.domain.entities.member import MemberCreateDTO, MemberDTO, MemberUpdateDTO, MemberWithReposDTO
from backend.src.domain.entities.git_repo import GitRepoDTO



class IMemberService(ABC):
    """
    Define member service behavior required by the application.

    This interface represents the contract for managing members and their
    relationships with repositories. It abstracts persistence and business logic
    related to member lifecycle and associations.
    """

    @abstractmethod
    def add_member(self, member: MemberCreateDTO) -> MemberDTO:
        """
        Create a new member.

        Args:
            member (MemberCreateDTO): Member create payload.

        Returns:
            MemberDTO: Created member DTO.
        """
        pass

    @abstractmethod
    def update_member(self, member: MemberUpdateDTO) -> MemberWithReposDTO:
        """
        Update an existing member.

        Args:
            member (MemberUpdateDTO): Member update payload.

        Returns:
            MemberWithReposDTO: Updated member with repositories DTO.
        """
        pass

    @abstractmethod
    def get_by_id(self, member_id: int) -> MemberDTO:
        """
        Retrieve a member by their ID.

        Args:
            member_id (int): The member's database ID.

        Returns:
            MemberDTO: The member data transfer object.
        """
        pass
    @abstractmethod
    def get_members_by_repo(self, repo: GitRepoDTO) -> List[MemberDTO]:
        """
        Fetch members associated with a repository.

        Args:
            repo (GitRepoDTO): Repository DTO used to resolve membership.

        Returns:
            List[MemberDTO]: List of member DTOs.
        """
        pass

    @abstractmethod
    def get_member_by_mail(self, mail: str) -> MemberWithReposDTO:
        """
        Fetch a member by email address.

        Args:
            mail (str): Member email.

        Returns:
            MemberWithReposDTO: Member DTO with repositories.
        """
        pass

    @abstractmethod
    def get_all_with_repos(self) -> List[MemberWithReposDTO]:
        """
        Return all members with their repositories.

        Returns:
            List[MemberWithReposDTO]: List of members with repositories.
        """
        pass

    @abstractmethod
    def delete(self, member_id: int) -> bool:
        """
        Delete a member by id.

        Args:
            member_id (int): Member identifier.

        Returns:
            bool: True when deletion succeeds.
        """
        pass