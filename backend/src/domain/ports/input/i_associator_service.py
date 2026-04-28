"""
Service port for associator operations.

This module defines the IAssociatorService interface, which specifies operations for managing
associations between repositories, ClickUp spaces, and repository members.

It acts as a contract for application-level services responsible for:
- Linking repositories with ClickUp spaces
- Managing repository members (add, remove, update)
"""

from abc import ABC, abstractmethod

from backend.src.domain.entities.associator import (
    AssociateClickUpSpaceRequest,
    AssociateClickUpSpaceResponse,
    AssociateMembersResponse,
    RepoMembersRequest,
)


class IAssociatorService(ABC):
    """
    Define associator service behavior required by the application.

    This interface represents the contract for managing associations between repositories,
    ClickUp spaces, and members. It abstracts the underlying implementation of integration
    and persistence concerns.
    """

    @abstractmethod
    def associate_clickup_space(self, request: AssociateClickUpSpaceRequest) -> AssociateClickUpSpaceResponse:
        """
        Associate a ClickUp space with a repository.

        Args:
            request (AssociateClickUpSpaceRequest): Association request payload.

        Returns:
            AssociateClickUpSpaceResponse: ClickUp space association response.
        """
        pass

    @abstractmethod
    def add_members(self, request: RepoMembersRequest) -> AssociateMembersResponse:
        """
        Add members to a repository.

        Args:
            request (RepoMembersRequest): Repository members request.

        Returns:
            AssociateMembersResponse: Members association response.
        """
        pass

    @abstractmethod
    def remove_members(self, request: RepoMembersRequest) -> AssociateMembersResponse:
        """
        Remove members from a repository.

        Args:
            request (RepoMembersRequest): Repository members request.

        Returns:
            AssociateMembersResponse: Members association response.
        """
        pass

    @abstractmethod
    def update_members(self, request: RepoMembersRequest) -> AssociateMembersResponse:
        """
        Replace repository members with the provided list.

        Args:
            request (RepoMembersRequest): Repository members request.

        Returns:
            AssociateMembersResponse: Members association response.
        """
        pass

