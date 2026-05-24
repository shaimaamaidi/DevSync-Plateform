"""
Dependency container for ClickUp workflow and backlog generation.

This module defines the ClickUpContainer class, which extends the base ClickUp
infrastructure container and wires together all components required for backlog
generation workflows.

It is responsible for initializing and exposing:
- ClickUp infrastructure (reader, writer, HTTP client)
- Workflow-related use cases (task management, structure, metadata, reading)
- Workspace orchestration services
- Factory methods for workflow-scoped use cases

This container is a central entry point for ClickUp-driven backlog generation
and task processing pipelines.

Classes:
    ClickUpContainer: Application/request-scoped dependency injection container.
"""

import logging

from backend.src.application.use_cases.clickup_space_task_reader_use_case import ClickUpSpaceTaskReaderUseCase
from backend.src.application.use_cases.clickup_structure_management_use_case import ClickUpStructureManagementUseCase
from backend.src.application.use_cases.clickup_structure_metadata_use_case import ClickUpStructureMetadataUseCase
from backend.src.application.use_cases.clickup_task_management_use_case import ClickUpTaskManagementUseCase
from backend.src.domain.exceptions.base.app_exception import AppException
from backend.src.domain.exceptions.system.service_unavailable_exception import ServiceUnavailableException
from backend.src.domain.ports.repositories.i_clickup_repository import IClickUpRepository
from backend.src.domain.ports.repositories.i_member_repository import IMemberRepository
from backend.src.infrastructure.di.base_clickup_container import BaseClickUpContainer

from backend.src.infrastructure.external.clickup.clickup_reader import ClickUpReader
from backend.src.infrastructure.external.clickup.writer.clickup_task_writer import ClickUpTaskWriter
from backend.src.infrastructure.external.clickup.client.clickup_http_client import ClickUpHttpClient
from backend.src.infrastructure.external.clickup.writer.clickup_workspace_writer import ClickUpWorkSpaceWriter


logger = logging.getLogger(__name__)


class ClickUpContainer(BaseClickUpContainer):
    """
    Application dependency container for ClickUp workflow orchestration.

    This container extends BaseClickUpContainer and enriches it with workflow-
    specific components required for backlog generation and task management.

    It coordinates initialization of:
    - ClickUp infrastructure clients (HTTP, reader, writer)
    - Workspace-level services (structure, metadata, task reading)
    - Task management services (create, update, delete)
    - Workflow orchestration use cases

    It also provides factory methods for dynamically created use cases
    that require request-scoped repositories.

    Attributes:
        clickup_writer (ClickUpTaskWriter | None):
            Infrastructure service for ClickUp task write operations.
        clickup_workspace_writer (ClickUpWorkSpaceWriter | None):
            Infrastructure service for ClickUp workspace-level write operations.
        http_client (ClickUpHttpClient):
            HTTP client used for ClickUp API communication.
        clickup_reader (ClickUpReader):
            Infrastructure service for reading ClickUp data.

        clickup_structure_metadata_use_case (ClickUpStructureMetadataUseCase | None):
            Use case for retrieving ClickUp workspace structure metadata.
        clickup_space_task_reader_use_case (ClickUpSpaceTaskReaderUseCase | None):
            Use case for reading tasks from a ClickUp space.
        clickup_task_creation_use_case (ClickUpTaskManagementUseCase | None):
            Use case for managing ClickUp tasks lifecycle.
    """

    def __init__(self):
        """
        Initialize the ClickUp workflow container.

        This constructor initializes base ClickUp infrastructure and then
        wires all workflow-related use cases required for backlog generation.

        Raises:
            AppException: If ClickUp infrastructure or workflow initialization fails.
        """
        logger.info("Initializing ClickUp container.")

        self.clickup_workspace_writer: ClickUpWorkSpaceWriter | None = None
        self.clickup_structure_metadata_use_case: ClickUpStructureMetadataUseCase | None = None
        self.clickup_space_task_reader_use_case: ClickUpSpaceTaskReaderUseCase | None = None
        self.clickup_task_creation_use_case: ClickUpTaskManagementUseCase | None = None

        try:
            super().__init__()
            self._init_clickup_workspace_writer()
            self._init_clickup_structure_metadata_use_case()
            self._init_clickup_space_task_reader_use_case()
            self._init_clickup_task_creation_use_case()

            logger.info("ClickUp container initialized successfully.")

        except AppException:
            raise
        except Exception as e:
            logger.exception("Failed to initialize ClickUp container.")
            raise AppException(
                "ClickUp services are currently unavailable. Please try again later.",
                "CLICKUP_CONTAINER_INIT_ERROR",
                http_status=500,
            ) from e

    def _init_clickup_workspace_writer(self):
        """
        Initialize ClickUp workspace writer service.

        This method sets up the infrastructure component responsible for
        writing workspace-level data to ClickUp, such as structure creation
        or updates.
        """
        logger.info("Initializing ClickUp external service.")

        self.clickup_workspace_writer = ClickUpWorkSpaceWriter(self.http_client)

    def _init_clickup_structure_metadata_use_case(self):
        """
        Initialize ClickUpStructureMetadataUseCase.

        This use case retrieves ClickUp workspace structure metadata such as:
        - Spaces
        - Folders
        - Lists
        - Status configurations

        It relies on ClickUpReader to fetch data from ClickUp API.
        """
        logger.info("Initializing ClickUpStructureMetadataUseCase.")

        self.clickup_structure_metadata_use_case = ClickUpStructureMetadataUseCase(
            self.clickup_reader
        )

    def _init_clickup_task_creation_use_case(self):
        """
        Initialize ClickUpTaskManagementUseCase.

        This use case manages ClickUp task lifecycle operations including:
        - Task creation
        - Task updates
        - Task deletion

        It depends on:
        - ClickUpTaskWriter for write operations
        - ClickUpReader for workspace and context retrieval
        """
        logger.info("Initializing ClickUpTaskManagementUseCase.")

        self.clickup_task_creation_use_case = ClickUpTaskManagementUseCase(
            self.clickup_writer,
            self.clickup_reader,
        )

    def _init_clickup_space_task_reader_use_case(self):
        """
        Initialize ClickUpSpaceTaskReaderUseCase.

        This use case provides read-only access to tasks inside a ClickUp space.
        It retrieves task data without applying business transformations.
        """
        logger.info("Initializing ClickUpSpaceTaskReaderUseCase.")

        self.clickup_space_task_reader_use_case = ClickUpSpaceTaskReaderUseCase(
            self.clickup_reader
        )

    def create_clickup_structure_creation_use_case(self, clickup_repo: IClickUpRepository, member_repo: IMemberRepository) -> ClickUpStructureManagementUseCase:
        """
        Factory method for ClickUpStructureManagementUseCase.

        This method builds a use case responsible for creating and managing
        ClickUp workspace structure.

        It combines:
        - ClickUp repository abstraction
        - Member repository for assignment resolution
        - ClickUp workspace writer infrastructure

        Args:
            clickup_repo: Request-scoped ClickUp repository abstraction.
            member_repo: Request-scoped member repository abstraction.

        Returns:
            ClickUpStructureManagementUseCase: Fully initialized use case.

        Raises:
            ServiceUnavailableException: If ClickUp writer infrastructure is not available.
        """
        if self.clickup_writer is None:
            raise ServiceUnavailableException("ClickUp service is currently unavailable. Please try again later.")

        return ClickUpStructureManagementUseCase(
            clickup_repo=clickup_repo,
            member_repo=member_repo,
            clickup_reader=self.clickup_reader,
            clickup_writer=self.clickup_workspace_writer
        )