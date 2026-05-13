"""
ClickUp workspace structure creation use case module.

This module provides the ClickUpStructureCreationUseCase class, which is responsible
for creating ClickUp workspace structure elements such as spaces, folders, lists,
and statuses.

It coordinates between the ClickUpWriter (infrastructure adapter) and the
ClickUpService (application state management) to ensure proper creation and
persistence of workspace structure entities.

Classes:
    ClickUpStructureCreationUseCase: Use case for creating ClickUp workspace structures.
"""

import logging

from backend.src.domain.entities.clickup.add_status_request import AddStatusRequest
from backend.src.domain.entities.clickup.create_folder_request import CreateFolderRequest
from backend.src.domain.entities.clickup.create_list_request import CreateListRequest
from backend.src.domain.entities.clickup.create_space_request import CreateSpaceRequest
from backend.src.domain.entities.clickup.folder_with_list_metadata import FolderWithListsMetadata
from backend.src.domain.entities.clickup.list_metadata import ClickUpListMetadata
from backend.src.domain.entities.clickup.status import ClickUpStatus
from backend.src.domain.entities.clickup_space import ClickUpSpaceCreateDTO, ClickUpSpaceDTO, ClickUpSpaceRegisterDTO
from backend.src.domain.exceptions.clickup.clickup_space_name_mismatch_exception import \
    ClickUpSpaceNameMismatchException
from backend.src.domain.exceptions.common.invalid_input_exception import InvalidInputException
from backend.src.domain.ports.input.i_clickup_structure_creation_use_case import IClickUpStructureCreationUseCase
from backend.src.domain.ports.output.clickup.i_clickup_reader import IClickUpReader
from backend.src.domain.ports.output.clickup.i_clickup_workspace_writer import IClickUpWorkSpaceWriter
from backend.src.domain.ports.repositories.i_clickup_repository import IClickUpRepository

logger = logging.getLogger(__name__)


class ClickUpStructureCreationUseCase(IClickUpStructureCreationUseCase):
    """
    Application use case for creating ClickUp workspace structure.

    This class is responsible for orchestrating creation operations such as:
    - Creating spaces
    - Creating folders
    - Creating lists
    - Adding statuses to lists

    It delegates API operations to the ClickUpWriter port and persists or
    registers domain-level data through ClickUpService when needed.

    Attributes:
        _clickup_repo (IClickUpRepository): ClickUp persistence port.
        _clickup_writer (IClickUpWorkSpaceWriter): Infrastructure port for ClickUp API writes.
    """

    def __init__(self, clickup_repo: IClickUpRepository, clickup_reader: IClickUpReader, clickup_writer: IClickUpWorkSpaceWriter):
        """
        Initialize the use case with a clickup service and workspace port.

        Args:
            clickup_repo (IClickUpService): Service responsible for domain persistence logic.
            clickup_reader (IClickUpReader): Reader port for ClickUp API operations.
            clickup_writer (IClickUpWorkSpaceWriter): Writer port for ClickUp API operations.
        """
        self._clickup_repo = clickup_repo
        self._clickup_reader = clickup_reader
        self._clickup_writer = clickup_writer

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
        logger.info("Registering ClickUp space. space_code=%s.", space.space_code)

        if not space.space_code or not space.name:
            logger.warning(
                "Invalid input for clickup space creation (name=%s, space_code=%s).",
                space.name,
                space.space_code
            )
            raise InvalidInputException(
                "ClickUp space must have a valid 'name' and 'space_code' for register."
            )
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

        Args:
            space (CreateSpaceRequest): Request DTO containing space creation data.

        Returns:
            ClickUpSpaceDTO: Created space DTO.
        """
        logger.info("Creating ClickUp space. space_name=%s.", space.space_name)

        if not space.space_name:
            logger.warning(
                "Invalid input for clickup space creation (name=%s, space_code=%s).",
                space.space_name,
            )
            raise InvalidInputException(
                "ClickUp space must have a valid 'name' for create."
            )

        space_code, space_name = self._clickup_writer.create_space(space.space_name)

        logger.info(
            "ClickUp space created successfully via API. space_id=%s name=%s.",
            space_code,
            space_name,
        )

        result = self._clickup_repo.save(ClickUpSpaceCreateDTO(name=space_name, space_code=space_code))

        logger.info(
            "ClickUp space persisted successfully. space_id=%s.",
            space_code,
        )

        return result

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