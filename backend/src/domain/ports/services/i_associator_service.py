"""
Service port for repository association workflows.

This module defines the IAssociatorService interface, which specifies operations for associating repositories, members, and ClickUp spaces.
"""

from abc import ABC, abstractmethod
from typing import List
from backend.src.domain.entities.git_repo import GitRepoDTO
from backend.src.domain.entities.member import MemberDTO


class IAssociatorService(ABC):
    """
    Define association operations for repositories, members, and ClickUp spaces.
    """
    @abstractmethod
    def associate_space(self, repo: GitRepoDTO, space_name: str, space_code: str):
        """Associate a ClickUp space by name and code.

        Args:
            repo: Repository DTO.
            space_name: ClickUp space name.
            space_code: ClickUp space code.
        """
        pass

    @abstractmethod
    def associate_members(self, repo: GitRepoDTO, members_data: List[dict]) -> List[MemberDTO]:
        """Associate members to a repository.

        Args:
            repo: Repository DTO.
            members_data: List of member payloads.

        Returns:
            List of member DTOs.
        """
        pass
        
    @abstractmethod
    def associate_clickup_space(self, repo_url: str, space_code: str):
        """Associate a ClickUp space by repository URL.

        Args:
            repo_url: Repository URL.
            space_code: ClickUp space code.
        """
        pass
        
    @abstractmethod
    def add_members(self, repo_url: str, members: List[MemberDTO]):
        """Add members to a repository.

        Args:
            repo_url: Repository URL.
            members: Member DTO list.
        """
        pass

    @abstractmethod
    def remove_members(self, repo_url: str, members: List[MemberDTO]):
        """Remove members from a repository.

        Args:
            repo_url: Repository URL.
            members: Member DTO list.
        """
        pass

    @abstractmethod
    def update_members(self, repo_url: str, members: List[MemberDTO]):
        """Replace repository members.

        Args:
            repo_url: Repository URL.
            members: Member DTO list.
        """
        pass        
