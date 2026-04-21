"""
Repository port for member persistence.

This module defines the IMemberRepository interface, which specifies persistence operations
for member entities, including authentication data retrieval, creation, update, lookup, and deletion.
"""

from abc import ABC, abstractmethod
from typing import List

from backend.src.domain.entities.member import (
    MemberCreateDTO,
    MemberDTO,
    MemberUpdateDTO,
    MemberWithReposDTO,
    MemberCredentialsDTO,
)


class IMemberRepository(ABC):
    """
    Define persistence operations for members.

    This interface represents the contract for storing, retrieving, and managing member data
    in a persistence layer such as a database, including relations with repositories.
    """

    @abstractmethod
    def find_credentials_by_mail(self, mail: str) -> MemberCredentialsDTO:
        """
        Retrieve member credentials by email address.

        Args:
            mail (str): Member email address.

        Returns:
            MemberCredentialsDTO: Credentials required for authentication.
        """
        pass

    @abstractmethod
    def save(self, member: MemberCreateDTO) -> MemberDTO:
        """
        Persist a new member.

        Args:
            member (MemberCreateDTO): Member creation data.

        Returns:
            MemberDTO: Created member.
        """
        pass

    @abstractmethod
    def update(self, member: MemberUpdateDTO) -> MemberWithReposDTO:
        """
        Update an existing member.

        Args:
            member (MemberUpdateDTO): Member update data.

        Returns:
            MemberWithReposDTO: Updated member with associated repositories.
        """
        pass

    @abstractmethod
    def find_by_id(self, member_id: int) -> MemberDTO:
        """
        Retrieve a member by its identifier.

        Args:
            member_id (int): Member identifier.

        Returns:
            MemberDTO: Member data.
        """
        pass

    @abstractmethod
    def find_by_mail(self, mail: str) -> MemberWithReposDTO:
        """
        Retrieve a member by email.

        Args:
            mail (str): Member email address.

        Returns:
            MemberWithReposDTO: Member with associated repositories.
        """
        pass

    @abstractmethod
    def find_by_repo_id(self, repo_id: int) -> List[MemberDTO]:
        """
        Retrieve members associated with a repository.

        Args:
            repo_id (int): Repository identifier.

        Returns:
            List[MemberDTO]: List of members.
        """
        pass

    @abstractmethod
    def find_all_with_repos(self) -> List[MemberWithReposDTO]:
        """
        Retrieve all members with their associated repositories.

        Returns:
            List[MemberWithReposDTO]: List of all members with repositories.
        """
        pass

    @abstractmethod
    def delete(self, member_id: int) -> bool:
        """
        Delete a member by its identifier.

        Args:
            member_id (int): Member identifier.

        Returns:
            bool: True if deletion succeeds, otherwise False.
        """
        pass