"""
ClickUp workspace writer adapter for applying workspace structure operations.

This module defines the ClickUpWorkSpaceWriter class, which implements the
IClickUpWorkSpaceWriter port. It is responsible for creating and configuring
ClickUp workspace structure elements such as Spaces, Folders, Lists, and
custom statuses.

This adapter acts as an infrastructure layer component translating domain-level
workspace structure decisions into ClickUp API requests.
"""

import logging
from typing import Optional, List

from backend.src.domain.entities.clickup.list import ClickUpList
from backend.src.domain.entities.clickup.status import ClickUpStatus
from backend.src.domain.exceptions.clickup.clickup_write_exception import ClickUpWriteException
from backend.src.domain.ports.output.clickup.i_clickup_workspace_writer import IClickUpWorkSpaceWriter
from backend.src.infrastructure.external.clickup.client.clickup_http_client import ClickUpHttpClient


logger = logging.getLogger(__name__)


class ClickUpWorkSpaceWriter(IClickUpWorkSpaceWriter):
    """
    ClickUp infrastructure adapter for writing workspace structure changes.

    This class centralizes workspace provisioning operations:
    - Creation of Spaces inside a ClickUp Workspace (Team)
    - Creation of Folders inside a Space
    - Creation of Lists inside a Folder or directly inside a Space
    - Configuration of custom statuses on Lists

    It ensures synchronization between domain-level workspace structure
    definitions and ClickUp workspace state.

    Attributes:
        _http (ClickUpHttpClient): HTTP client used for ClickUp API communication.
    """

    def __init__(self, http_client: ClickUpHttpClient):
        """
        Initialize the workspace writer with an HTTP client.

        Args:
            http_client: ClickUp HTTP client instance used for API calls.
        """
        self._http = http_client

    def create_space(self, name: str) -> tuple[str, str]:
        """
        Create a new Space in the ClickUp workspace.

        Args:
            name: Name of the Space to create.

        Returns:
            tuple[str, str]: A tuple containing the created Space ID and name.

        Raises:
            ClickUpWriteException: If the API request fails.
        """
        logger.info("Creating Space. name=%s.", name)

        endpoint = f"/team/{self._http.team_id}/space"
        payload = {"name": name}

        response = self._http.post_raw(endpoint, payload)

        if response.status_code == 200:
            data = response.json()
            logger.info(
                "Space created successfully. name=%s status_code=%d.",
                name,
                response.status_code,
            )
            return data["id"], data["name"]

        logger.error(
            "Space creation failed. name=%s status_code=%d response=%s.",
            name,
            response.status_code,
            response.text,
        )
        raise ClickUpWriteException(
            f"Failed to create space '{name}' "
            f"(status {response.status_code}) — {response.text}"
        )

    def create_folder(self, space_id: str, name: str) -> tuple[str, str]:
        """
        Create a new Folder inside a Space.

        Args:
            space_id: ClickUp Space identifier.
            name: Name of the Folder to create.

        Returns:
            tuple[str, str]: A tuple containing the created folder ID and name.

        Raises:
            ClickUpWriteException: If the API request fails.
        """
        logger.info("Creating Folder. name=%s space_id=%s.", name, space_id)

        endpoint = f"/space/{space_id}/folder"
        payload = {"name": name}

        response = self._http.post_raw(endpoint, payload)

        if response.status_code == 200:
            data = response.json()
            logger.info(
                "Folder created successfully. name=%s status_code=%d.",
                name,
                response.status_code,
            )
            return data["id"],data["name"]

        logger.error(
            "Folder creation failed. name=%s status_code=%d response=%s.",
            name,
            response.status_code,
            response.text,
        )
        raise ClickUpWriteException(
            f"Failed to create folder '{name}' "
            f"(status {response.status_code}) — {response.text}"
        )

    def create_list(
        self,
        space_id: str,
        name: str = "List",
        folder_id: Optional[str] = None,
    ) -> ClickUpList:
        """
        Create a new List in ClickUp.

        The list can be created either:
        - inside a Folder (if folder_id is provided)
        - directly inside a Space (folderless list)

        Args:
            space_id: ClickUp Space identifier.
            name: Name of the List to create.
            folder_id: Optional Folder identifier.

        Returns:
            ClickUpList: A domain object representing the created List, including
                its ID, name, statuses, and priorities.

        Raises:
            ClickUpWriteException: If the API request fails.
        """
        if folder_id:
            logger.info(
                "Creating List inside Folder. name=%s folder_id=%s.", name, folder_id
            )
            endpoint = f"/folder/{folder_id}/list"
        else:
            logger.info(
                "Creating folderless List inside Space. name=%s space_id=%s.", name, space_id
            )
            endpoint = f"/space/{space_id}/list"

        payload = {"name": name}

        response = self._http.post_raw(endpoint, payload)

        if response.status_code == 200:
            data = response.json()
            logger.info(
                "List created successfully. name=%s status_code=%d.",
                name,
                response.status_code,
            )
            return ClickUpList(
                id=data["id"],
                name=data["name"],
                tasks=[],
                statuses=[s["status"] for s in data.get("statuses", [])],
                priorities=[p["priority"] for p in
                            data.get("features", {}).get("priorities", {}).get("priorities", [])],
            )

        logger.error(
            "List creation failed. name=%s status_code=%d response=%s.",
            name,
            response.status_code,
            response.text,
        )
        raise ClickUpWriteException(
            f"Failed to create list '{name}' "
            f"(status {response.status_code}) — {response.text}"
        )

    def add_status_to_list(
        self,
        list_id: str,
        status: ClickUpStatus,
    ) -> List[str]:
        """
        Add a single status to an existing List without affecting other statuses.

        Fetches the current statuses from ClickUp, appends the new one,
        then sends a full replacement PUT request.

        Args:
            list_id: The ClickUp List ID to update.
            status: The new ClickUpStatus to add.

        Returns:
            List[str]: The updated list of status names after adding the new status.

        Raises:
            ClickUpWriteException: If the PUT request fails.
        """
        logger.info(
            "Fetching current statuses for List. list_id=%s.", list_id
        )

        current = self._http.get(f"/list/{list_id}")
        existing_statuses = current.get("statuses", [])

        merged = existing_statuses + [status.to_dict()]

        logger.info(
            "Adding status to List. list_id=%s status=%s existing_count=%d.",
            list_id,
            status.status,
            len(existing_statuses),
        )

        response = self._http.put_raw(f"/list/{list_id}", {"statuses": merged})

        if response.status_code == 200:
            logger.info(
                "Status added successfully. list_id=%s status=%s status_code=%d.",
                list_id,
                status.status,
                response.status_code,
            )
            list_status = []
            for status in merged:
                list_status.append(status.get("status"))
            return list_status

        logger.error(
            "Status add failed. list_id=%s status=%s status_code=%d response=%s.",
            list_id,
            status.status,
            response.status_code,
            response.text,
        )
        raise ClickUpWriteException(
            f"Failed to add status '{status.status}' to list '{list_id}' "
            f"(status {response.status_code}) — {response.text}"
        )