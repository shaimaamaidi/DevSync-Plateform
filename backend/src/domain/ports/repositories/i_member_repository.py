"""
Repository port for member persistence.

This module defines the IMemberRepository interface, which specifies persistence operations
for member entities, including authentication data retrieval, creation, update, lookup, and deletion.
"""

from abc import ABC, abstractmethod
from typing import List, Dict

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
    def find_by_arabic_name(self, arabic_names: list[str], ignore_names) -> Dict[str, str]:
        """
        Fetch members by their Arabic names and return a mapping to their emails.

        This method resolves a list of Arabic names into a dictionary mapping
        normalized names to email addresses. If some names cannot be resolved,
        behavior depends on the `ignore_names` flag.

        Args:
            arabic_names (list[str]): List of Arabic names to resolve into members.
            ignore_names (bool):
                If True, unresolved names are ignored.
                If False, an exception is raised when some names are not found.

        Returns:
            Dict[str, str]: Mapping of normalized Arabic name to member email.
        """
        pass

    @abstractmethod
    def find_by_mails(self, mails: list[str]) -> Dict[str, str]:
        """
        Fetch members by their mails and return a mapping to their arabic names.

        This method resolves a list of mails into a dictionary mapping
        normalized mail to arabic names. If some names cannot be resolved,
        then we ignore them.

        Args:
            mails (list[str]): List of mails to resolve into members.

        Returns:
            Dict[str, str]: Mapping of normalized mails to arabic names.

        Raises:
            MemberPersistenceException: If a database error occurs during the query.
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