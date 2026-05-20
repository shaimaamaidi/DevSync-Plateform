"""
ClickUp workspace structure management use case module.

This module provides the ClickUpStructureCreationUseCase class, which is
responsible for managing ClickUp workspace structure operations such as:

- Registering existing ClickUp spaces
- Creating and deleting ClickUp spaces
- Creating folders and lists
- Adding statuses to lists
- Inviting and removing workspace members

The use case coordinates interactions between ClickUp infrastructure
ports and persistence repositories to ensure consistency between the
application database and ClickUp resources.

It also applies compensation mechanisms when partial failures occur
during synchronization between ClickUp and the persistence layer.

Classes:
    ClickUpStructureCreationUseCase: Use case for managing ClickUp workspace structures and members.
"""

import logging

from backend.src.domain.entities.clickup.add_status_request import AddStatusRequest
from backend.src.domain.entities.clickup.create_folder_request import CreateFolderRequest
from backend.src.domain.entities.clickup.create_list_request import CreateListRequest
from backend.src.domain.entities.clickup.create_space_request import CreateSpaceRequest
from backend.src.domain.entities.clickup.folder_with_list_metadata import FolderWithListsMetadata
from backend.src.domain.entities.clickup.list_metadata import ClickUpListMetadata
from backend.src.domain.entities.clickup.member_invitation import ClickUpMemberInvitation
from backend.src.domain.entities.clickup.status import ClickUpStatus
from backend.src.domain.entities.clickup_space import ClickUpSpaceCreateDTO, ClickUpSpaceDTO, ClickUpSpaceRegisterDTO, \
    ClickUpSpaceDetailDTO, ClickUpSpaceUpdateDTO, ClickUpRepoRefDTO
from backend.src.domain.exceptions.clickup.clickup_persistence_exception import ClickUpPersistenceException
from backend.src.domain.exceptions.clickup.clickup_space_name_mismatch_exception import \
    ClickUpSpaceNameMismatchException
from backend.src.domain.exceptions.clickup.clickup_space_not_found_exception import ClickUpSpaceNotFoundException
from backend.src.domain.exceptions.clickup.clickup_write_exception import ClickUpWriteException
from backend.src.domain.exceptions.common.invalid_input_exception import InvalidInputException
from backend.src.domain.exceptions.member.member_not_found_exception import MemberNotFoundException
from backend.src.domain.ports.input.i_clickup_structure_creation_use_case import IClickUpStructureCreationUseCase
from backend.src.domain.ports.output.clickup.i_clickup_reader import IClickUpReader
from backend.src.domain.ports.output.clickup.i_clickup_workspace_writer import IClickUpWorkSpaceWriter
from backend.src.domain.ports.repositories.i_clickup_repository import IClickUpRepository
from backend.src.domain.ports.repositories.i_member_repository import IMemberRepository


logger = logging.getLogger(__name__)


class ClickUpStructureCreationUseCase(IClickUpStructureCreationUseCase):
    """
    Application use case for managing ClickUp workspace structures.

    This class orchestrates workspace-related operations such as:

    - Registering existing ClickUp spaces
    - Creating and deleting spaces
    - Creating folders and lists
    - Adding statuses to lists
    - Inviting and removing workspace members

    It delegates ClickUp API operations to dedicated infrastructure ports
    and persists domain entities through repository ports.

    The use case also applies validation and compensation logic to maintain
    consistency between the application database and ClickUp resources.

    Attributes:
        _clickup_repo (IClickUpRepository): Repository port used for ClickUp space persistence.
        _member_repo (IMemberRepository): Repository port used for member retrieval.
        _clickup_reader (IClickUpReader): Reader port used for ClickUp read operations.
        _clickup_writer (IClickUpWorkSpaceWriter): Writer port used for ClickUp write operations.
    """

    def __init__(
        self,
        clickup_repo: IClickUpRepository,
        member_repo: IMemberRepository,
        clickup_reader: IClickUpReader,
        clickup_writer: IClickUpWorkSpaceWriter
    ):
        """
        Initialize the use case with a clickup service and workspace port.

        Args:
            clickup_repo (IClickUpService): Service responsible for click up space persistence.
            member_repo (IMemberRepository): Repository port for member retrieval operations.
            clickup_reader (IClickUpReader): Reader port for ClickUp API operations.
            clickup_writer (IClickUpWorkSpaceWriter): Writer port for ClickUp API operations.
        """
        self._clickup_repo = clickup_repo
        self._member_repo = member_repo
        self._clickup_reader = clickup_reader
        self._clickup_writer = clickup_writer

    def register_space(self, space: ClickUpSpaceRegisterDTO) -> ClickUpSpaceDTO:
        """
        Validate an existing ClickUp space and persist it in the database.

        This method verifies that the provided space exists in ClickUp,
        validates the provided name against the actual ClickUp space name,
        and persists the space in the application database.

        Args:
            space (ClickUpSpaceRegisterDTO): Request DTO containing space registration data.

        Returns:
            ClickUpSpaceDTO: Persisted ClickUp space DTO.

        Raises:
            ClickUpSpaceNameMismatchException: If the provided name does not match the ClickUp space name.
        """
        logger.info("Registering ClickUp space. space_code=%s.", space.space_code)

        existing_by_name = self._clickup_repo.find_by_name(space.name)

        if existing_by_name:
            raise InvalidInputException(
                f"A ClickUp space with name '{space.name}' already exists."
            )

        try:
            existing_by_code = self._clickup_repo.find_by_space_code(space.space_code)
            if existing_by_code:
                raise InvalidInputException(
                    f"A ClickUp space with ID '{space.space_code}' is already registered."
                )
        except ClickUpSpaceNotFoundException:
            pass

        space_name = self._clickup_reader.space_exists(space.space_code)

        if space.name and (space_name.strip().lower() != space.name.strip().lower()) and  (not space.ignore_name):
            logger.warning(
                "Space name mismatch. space_code=%s expected=%s actual=%s.",
                space.space_code,
                space.name,
                space_name,
            )
            raise ClickUpSpaceNameMismatchException(expected=space.name, actual=space_name)

        result = self._clickup_repo.save(ClickUpSpaceCreateDTO(name=space_name, space_code=space.space_code))

        logger.info("ClickUp space registered successfully. space_id=%s.", space.space_code)

        return result


    def create_space(self, space: CreateSpaceRequest) -> ClickUpSpaceDTO:
        """
        Create a ClickUp space and persist it in the application layer.

        If database persistence fails after successful ClickUp creation,
        a compensation action is triggered to delete the created space
        from ClickUp.

        Args:
            space (CreateSpaceRequest): Request DTO containing space creation data.

        Returns:
            ClickUpSpaceDTO: Created space DTO.

        Raises:
            ClickUpPersistenceException: If persistence fails after successful ClickUp creation.
        """
        logger.info("Creating ClickUp space. space_name=%s.", space.space_name)

        existing = self._clickup_repo.find_by_name(space.space_name)
        if existing:
            raise InvalidInputException(
                f"A ClickUp space named '{space.space_name}' already exists."
            )

        space_code, space_name = self._clickup_writer.create_space(space.space_name)

        logger.info(
            "ClickUp space created successfully via API. space_id=%s name=%s.",
            space_code,
            space_name,
        )

        try:
            result = self._clickup_repo.save(ClickUpSpaceCreateDTO(name=space_name, space_code=space_code))

            logger.info(
                "ClickUp space persisted successfully. space_id=%s.",
                space_code,
            )

            return result
        except (InvalidInputException, ClickUpPersistenceException) as e:
            logger.error(
                "DB persistence failed after ClickUp space creation. "
                "Attempting compensation (delete from ClickUp). space_code=%s.",
                space_code,
            )
            self._compensate_creation_clickup_space(space_code)
            raise

    def delete_space(self, space_id: int) -> bool:
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
        logger.info("Deleting ClickUp space. space_id=%s.", space_id)

        clickup_space = self._clickup_repo.find_by_id(space_id)

        self._clickup_repo.delete(clickup_space.id)
        try:
            result = self._clickup_writer.delete_space(clickup_space.space_code)

            logger.info(
                "ClickUp space deleted successfully. space_code=%s.",
                clickup_space.space_code,
            )

            return result
        except ClickUpWriteException as e:
            if "not found" in str(e).lower() or "404" in str(e):
                logger.warning(
                    "Space already absent from ClickUp, DB deletion kept. space_code=%s.",
                    clickup_space.space_code,
                )
                return True
            logger.error(
                "ClickUp API deletion failed after DB deletion. "
                "Attempting compensation (re-insert in DB). space_code=%s.",
                clickup_space.space_code,
            )
            self._compensate_space_reinsert(clickup_space)
            raise


    def create_folder(self, folder: CreateFolderRequest) -> FolderWithListsMetadata:
        """
        Create a folder inside a ClickUp space.

        Args:
            folder (CreateFolderRequest): Request DTO containing folder creation data.

        Returns:
            FolderWithListsMetadata: Created folder metadata.
        """
        logger.info(
            "Creating folder in ClickUp space. space_id=%s folder_name=%s.",
            folder.space_id,
            folder.name,
        )

        folder_id, folder_name = self._clickup_writer.create_folder(folder.space_id, folder.name)

        logger.info(
            "Folder created successfully. space_id=%s folder_id=%s folder_name=%s.",
            folder.space_id,
            folder_id,
            folder_name,
        )

        return FolderWithListsMetadata(
            id=folder_id,
            name=folder_name,
            lists=[]
        )

    def create_list(self, list_to_add: CreateListRequest)-> ClickUpListMetadata:
        """
        Create a list inside a ClickUp space or folder.

        Args:
            list_to_add (CreateListRequest): Request DTO containing list creation data.

        Returns:
            ClickUpListMetadata: Created list metadata.
        """
        logger.info(
            "Creating list in ClickUp. space_id=%s folder_id=%s list_name=%s.",
            list_to_add.space_id,
            list_to_add.folder_id,
            list_to_add.name,
        )

        result = self._clickup_writer.create_list(list_to_add.space_id, list_to_add.name, list_to_add.folder_id)

        logger.info(
            "List created successfully. list_id=%s list_name=%s.",
            result.id,
            result.name,
        )

        return result

    def add_status(self, status: AddStatusRequest) -> ClickUpListMetadata:
        """
        Add a status to a ClickUp list.

        Args:
            status (AddStatusRequest): Request DTO containing list ID and status data.

        Returns:
            ClickUpListMetadata: Updated list metadata.
        """
        logger.info(
            "Adding status to ClickUp list. list_id=%s status=%s.",
            status.list_id,
            status.status,
        )

        status_obj = ClickUpStatus(status.status, status.color, status.type)
        result = self._clickup_writer.add_status_to_list(status.list_id, status_obj)

        logger.info(
            "Status added successfully to list. list_id=%s.",
            result.id,
        )

        return result

    def invite_member(self, member: ClickUpMemberInvitation) -> bool:
        """
        Invite a member to a ClickUp workspace.

        Args:
            member (ClickUpMemberInvitation): Invitation request containing workspace member data.

        Returns:
            bool: True if the invitation succeeds.
        """
        logger.info(
            "Inviting member to ClickUp workspace. "
            "email=%s role=%s.",
            member.email,
            member.role,
        )

        result = self._clickup_writer.add_workspace_member(member)

        logger.info(
            "Member invited successfully to ClickUp workspace. "
            "email=%s.",
            member.email,
        )

        return result

    def remove_member_from_workspace(self, member_id: int) -> bool:
        """
        Remove a member from the ClickUp workspace.

        Args:
            member_id (int): member identifier in BDD.

        Returns:
            bool: True if the invitation succeeds.
        """
        logger.info(
            "Removing member from ClickUp workspace. "
            "member_id=%s.",
            member_id,
        )

        db_member = self._member_repo.find_by_id(member_id)

        if not db_member:
            raise MemberNotFoundException("Member not found. Please verify the provided information.")

        members = self._clickup_reader.get_workspace_members_with_roles()

        coord_member = next(
            (m for m in members if m["email"].lower() == db_member.mail.lower()),
            None
        )

        if not coord_member:
            logger.warning(
                "Member not found in ClickUp workspace, skipping ClickUp deletion. "
                "member_id=%s email=%s.",
                db_member.member_id,
                db_member.mail,
            )
            raise MemberNotFoundException("This member is not part of the ClickUp workspace.")

        result = self._clickup_writer.remove_workspace_member(coord_member["id"])

        logger.info(
            "Member removed successfully from ClickUp workspace. "
            "member_id=%s.",
            member_id,
        )

        return result


    def _compensate_creation_clickup_space(self, space_code: str) -> None:
        """
        Compensation action for failed database persistence.

        This method attempts to delete a ClickUp space that was successfully
        created in ClickUp but failed to persist in the application database.

        Args:
            space_code (str):
                ClickUp space identifier.
        """
        try:
            self._clickup_writer.delete_space(space_code)
            logger.info(
                "Compensation successful: ClickUp space deleted. space_code=%s.",
                space_code,
            )
        except Exception:
            logger.critical(
                "COMPENSATION FAILED: ClickUp space could not be deleted after DB error. "
                "Manual intervention required. space_code=%s.",
                space_code,
                exc_info=True,
            )

    def _compensate_space_reinsert(self, clickup_space: ClickUpSpaceDetailDTO) -> None:
        """
        Compensation action for failed ClickUp deletion.

        This method attempts to restore a ClickUp space in the database
        when deletion from ClickUp fails after the database record was removed.

        Args:
            clickup_space (ClickUpSpaceDetailDTO): Space DTO to restore in persistence storage.
        """
        try:
            result = self._clickup_repo.save(
                ClickUpSpaceCreateDTO(
                    name=clickup_space.name,
                    space_code=clickup_space.space_code,
                )
            )
            if clickup_space.repo:
                self._clickup_repo.update(
                    ClickUpSpaceUpdateDTO(
                        id=result.id,
                        repo=ClickUpRepoRefDTO(id=clickup_space.repo.id, url=clickup_space.repo.url),
                    )
                )
            logger.info(
                "Compensation successful: space re-inserted in DB. space_code=%s.",
                clickup_space.space_code,
            )
        except Exception:
            logger.critical(
                "COMPENSATION FAILED: space could not be re-inserted in DB after ClickUp failure. "
                "Manual intervention required. space_code=%s db_id=%s.",
                clickup_space.space_code,
                clickup_space.id,
                exc_info=True,
            )