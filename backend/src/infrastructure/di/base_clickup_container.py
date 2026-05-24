"""
ClickUp dependency container for external infrastructure.

This module defines the BaseClickUpContainer class, which is responsible for
initializing and exposing ClickUp-related infrastructure components such as
HTTP clients, readers, and task writers.

It acts as a dedicated dependency container for all ClickUp integrations
used across the application (task retrieval, task creation, and updates).

Classes:
    BaseClickUpContainer: Container for ClickUp external dependencies.
"""

import logging
from backend.src.domain.exceptions.base.app_exception import AppException
from backend.src.infrastructure.external.clickup.clickup_reader import ClickUpReader
from backend.src.infrastructure.external.clickup.client.clickup_http_client import ClickUpHttpClient
from backend.src.infrastructure.external.clickup.writer.clickup_task_writer import ClickUpTaskWriter


logger = logging.getLogger(__name__)


class BaseClickUpContainer:
    """
    ClickUp dependency container.

    This container is responsible for initializing and managing all
    ClickUp-related infrastructure components required by the application.

    It centralizes the setup of:
    - HTTP client for ClickUp API communication
    - ClickUp reader for retrieving workspace data
    - ClickUp writer for creating and updating tasks

    This ensures a single point of initialization for all ClickUp services
    and simplifies dependency management across the system.
    """

    def __init__(self):
        """
        Initialize ClickUp infrastructure dependencies.

        This constructor creates and wires the ClickUp HTTP client, reader,
        and writer components used by the application.

        Raises:
            AppException: If any ClickUp infrastructure component fails to
            initialize, indicating that ClickUp services are unavailable.
        """
        try:
            self.http_client = ClickUpHttpClient()
            self.clickup_reader = ClickUpReader(self.http_client)
            self.clickup_writer = ClickUpTaskWriter(self.http_client)
        except Exception as e:
            logger.exception("Failed to initialize ClickUp infrastructure.")
            raise AppException(
                "Click up services are currently unavailable. Please try again later.",
                "CLICKUP_INIT_ERROR",
                http_status=500,
            ) from e