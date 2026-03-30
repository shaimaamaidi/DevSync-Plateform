"""
Repository port for member persistence.

This module defines the IMemberRepository interface, which specifies persistence operations for member entities.
"""

from abc import ABC, abstractmethod
from typing import List

from backend.src.domain.entities.member import MemberCreateDTO, MemberDTO, MemberUpdateDTO, MemberWithReposDTO, \
    MemberCredentialsDTO


class IMemberRepository(ABC):
    """
    Define persistence operations for members.
    """
    @abstractmethod
    def find_credentials_by_mail(self, mail: str) -> MemberCredentialsDTO:
        """
        Retrieve member credentials by email address.

        Args:
            mail: Member email address.

        Returns:
            MemberCredentialsDTO: Credentials for authentication (id, mail, hashed_password).
        """
        pass

    @abstractmethod
    def save(self, member: MemberCreateDTO) -> MemberDTO:
        """Persist a new member.

        Args:
            member: Member create DTO.

        Returns:
            Created member DTO.
        """
        pass

    @abstractmethod
    def update(self, member: MemberUpdateDTO) -> MemberWithReposDTO:
        """Persist updates for a member.

        Args:
            member: Member update DTO.

        Returns:
            Updated member with repositories.
        """
        pass

    @abstractmethod
    def find_by_id(self, member_id: int) -> MemberDTO:
        """Find a member by id.

        Args:
            member_id: Member id.

        Returns:
            Member DTO.
        """
        pass

    @abstractmethod
    def find_by_mail(self, mail: str) -> MemberWithReposDTO:
        """Find a member by email.

        Args:
            mail: Member email.

        Returns:
            Member with repositories.
        """
        pass

    @abstractmethod
    def find_by_repo_id(self, repo_id: int) -> List[MemberDTO]:
        """Find members by repository id.

        Args:
            repo_id: Repository id.

        Returns:
            List of member DTOs.
        """
        pass

    @abstractmethod
    def find_all_with_repos(self) -> List[MemberWithReposDTO]:
        """Return all members with repositories.

        Returns:
            List of members with repositories.
        """
        pass

    @abstractmethod
    def delete(self, member_id: int) -> bool:
        """Delete a member by id.

        Args:
            member_id: Member id.

        Returns:
            True when deletion succeeds.
        """
        pass
