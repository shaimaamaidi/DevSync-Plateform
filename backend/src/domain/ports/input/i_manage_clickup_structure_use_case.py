"""
Use case port for ClickUp workspace structure creation.

This module defines the IClickUpStructureCreationUseCase interface, which specifies
operations for creating ClickUp workspace structural elements such as spaces,
folders, lists, and statuses.

It acts as a contract for application-level use cases responsible for:
- Creating ClickUp spaces
- Creating folders inside spaces
- Creating lists inside spaces or folders
- Adding statuses to lists
"""

from abc import ABC, abstractmethod

from backend.src.domain.entities.clickup.add_status_request import AddStatusRequest
from backend.src.domain.entities.clickup.create_folder_request import CreateFolderRequest
from backend.src.domain.entities.clickup.create_list_request import CreateListRequest
from backend.src.domain.entities.clickup.create_space_request import CreateSpaceRequest
from backend.src.domain.entities.clickup.folder_with_list_metadata import FolderWithListsMetadata
from backend.src.domain.entities.clickup.list_metadata import ClickUpListMetadata
from backend.src.domain.entities.clickup.member_invitation import ClickUpMemberInvitation
from backend.src.domain.entities.clickup_space import ClickUpSpaceDTO, ClickUpSpaceRegisterDTO


class IManageClickUpStructureUseCase(ABC):
    """
    Define ClickUp workspace structure creation behavior required by the application.

    This interface represents the contract for creating and managing ClickUp
    structural components (spaces, folders, lists, statuses) while delegating
    infrastructure operations to external adapters.
    """

    @abstractmethod
    def register_space(self, space: ClickUpSpaceRegisterDTO) -> ClickUpSpaceDTO:
        """
        Validate a ClickUp space existence and persist it in the database.

        Args:
            space(ClickUpSpaceRegisterDTO): Request DTO containing space registration data.

        Returns:
            ClickUpSpaceDTO: Persisted space.

        Raises:
            ClickUpSpaceNameMismatchException: If the provided name does not match the
                ClickUp space name.
        """
        pass

    @abstractmethod
    def create_space(self, space: CreateSpaceRequest) -> ClickUpSpaceDTO:
        """
        Create a ClickUp space.

        Args:
            space (CreateSpaceRequest): Request DTO containing space creation data.

        Returns:
            ClickUpSpaceDTO: Created ClickUp space DTO.
        """
        pass

    @abstractmethod
    def delete_space(self, space_id: str) -> bool:
        """
        Delete a ClickUp space from both the database and ClickUp.

        This method first removes the space from the application database,
        then deletes it from ClickUp.

        If ClickUp deletion fails after database deletion, a compensation
        action is triggered to restore the space in the database.

        Args:
            space_id (str): ClickUp space identifier.

        Returns:
            bool: True if deletion succeeds.

        Raises:
            ClickUpSpaceNotFoundException:If the space does not exist in the database.
            ClickUpWriteException: If ClickUp deletion fails.
        """
        pass

    @abstractmethod
    def create_folder(self, folder: CreateFolderRequest) -> FolderWithListsMetadata:
        """
        Create a folder inside a ClickUp space.

        Args:
            folder (CreateFolderRequest): Request DTO containing folder creation data.

        Returns:
            FolderWithListsMetadata: Created folder metadata with empty lists.
        """
        pass

    @abstractmethod
    def create_list(self, list_to_add: CreateListRequest) -> ClickUpListMetadata:
        """
        Create a list inside a ClickUp space or folder.

        Args:
            list_to_add (CreateListRequest): Request DTO containing list creation data.

        Returns:
            ClickUpListMetadata: Created list metadata.
        """
        pass

    @abstractmethod
    def add_status(self, status: AddStatusRequest) ->ClickUpListMetadata:
        """
        Add a status to a ClickUp list.

        Args:
            status (AddStatusRequest): Request DTO containing list ID and status data.

        Returns:
            ClickUpListMetadata: Updated list metadata after adding status.
        """
        pass

    @abstractmethod
    def invite_member(self, member: ClickUpMemberInvitation) -> bool:
        """
        Invite a member to a ClickUp workspace.

        Args:
            member (ClickUpMemberInvitation): Invitation request containing workspace member data.

        Returns:
            bool: True if the invitation succeeds.
        """
        pass

    @abstractmethod
    def remove_member_from_workspace(self, member_id: int) -> bool:
        """
        Invite a member to a ClickUp workspace.

        Args:
            member_id (int): member identifier in BDD.

        Returns:
            bool: True if the invitation succeeds.
        """
        pass
