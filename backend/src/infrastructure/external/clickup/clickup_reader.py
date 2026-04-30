"""
ClickUp reader adapter for retrieving workspace structure and members.

This module defines the ClickUpReader class, which implements the IClickUpReader
port. It is responsible for fetching ClickUp space structure (folders, lists,
tasks) and workspace members using the ClickUp HTTP client.

This adapter acts as an infrastructure layer component translating ClickUp API
responses into domain entities.
"""

import logging
from typing import List

from backend.src.domain.entities.clickup.clickup_list import ClickUpList, ClickUpTask
from backend.src.domain.entities.clickup.folder import Folder
from backend.src.domain.exceptions.clickup.clickup_empty_space_exception import ClickUpEmptySpaceException
from backend.src.domain.exceptions.clickup.clickup_workspace_members_exception import ClickUpWorkspaceMembersException
from backend.src.domain.ports.output.clickup.i_clickup_reader import IClickUpReader
from backend.src.infrastructure.external.clickup.client.clickup_http_client import ClickUpHttpClient


logger = logging.getLogger(__name__)


PRIORITIES = ["urgent", "high", "normal", "low"]


class ClickUpReader(IClickUpReader):
    """
    ClickUp infrastructure adapter for reading workspace data.

    This class centralizes:
    - Retrieval of ClickUp space structure (folders, lists, tasks)
    - Retrieval of workspace members
    - Transformation of API responses into domain entities

    Attributes:
        _http (ClickUpHttpClient): HTTP client used for API communication.
    """

    def __init__(self, http_client: ClickUpHttpClient):
        """
        Initialize the reader with an HTTP client.

        Args:
            http_client: ClickUp HTTP client instance.
        """
        self._http = http_client

    def get_space_structure(self, space_id: str) -> List[Folder]:
        """
        Retrieve full ClickUp space structure.

        This includes folders, lists, and tasks, and maps them into domain entities.

        Args:
            space_id: ClickUp space identifier.

        Returns:
            List of Folder objects containing lists, tasks, statuses, and priorities.

        Raises:
            ClickUpEmptySpaceException: If the space has no folders.
        """
        logger.info("Fetching space structure for space_id='%s'.", space_id)

        folders_data = self._get_folders(space_id)

        if not folders_data:
            logger.warning("Empty ClickUp space. space_id=%s.", space_id)
            raise ClickUpEmptySpaceException(
                f"No folder found in space '{space_id}'."
            )

        folders: List[Folder] = []

        for folder_data in folders_data:
            logger.info("Processing folder '%s' (id=%s).", folder_data["name"], folder_data["id"])
            lists_data = self._get_lists(folder_data["id"])
            lists: List[ClickUpList] = []

            for list_data in lists_data:
                # Fetch list details for statuses and priorities
                list_details = self._get_list_details(list_data["id"])

                # Fetch tasks
                tasks_data = self._get_tasks(list_data["id"])
                tasks: List[ClickUpTask] = []

                for task in tasks_data:
                    tasks.append(
                        ClickUpTask(
                            id=task["id"],
                            name=task["name"],
                            description=task.get("description", ""),
                            status=task["status"]["status"],
                            assignee=task["assignees"][0]["username"] if task["assignees"] else None,
                            priority=task["priority"]["priority"] if task.get("priority") else None
                        )
                    )

                # Fetch list statuses
                statuses = [s["status"] for s in list_details.get("statuses", []) if "status" in s]

                # Fetch list priorities
                priorities = [
                    p.get("priority") or p.get("name")
                    for p in list_details.get("priorities", [])
                    if p.get("priority") or p.get("name")
                ]

                logger.info(
                    "List '%s': %d task(s), %d status(es).",
                    list_data["name"],
                    len(tasks),
                    len(statuses),
                )

                lists.append(
                    ClickUpList(
                        id=list_data["id"],
                        name=list_data["name"],
                        tasks=tasks,
                        statuses=statuses,
                        priorities=PRIORITIES
                    )
                )

            folders.append(
                Folder(
                    id=folder_data["id"],
                    name=folder_data["name"],
                    lists=lists
                )
            )
        logger.info(
            "ClickUp space structure completed. space_id=%s folders=%d.",
            space_id,
            len(folders),
        )

        return folders

    def get_workspace_members(self, space_id: str) -> List[dict]:
        """
        Retrieve ClickUp workspace members.

        Args:
            space_id: ClickUp space identifier.

        Returns:
            List of member dictionaries with id, username, and email.

        Raises:
            ClickUpWorkspaceMembersException: If the workspace has no members.
        """
        logger.info("Fetching workspace members for space_id='%s'.", space_id)

        teams = self._http.get(f"/team").get("teams", [])
        members = []

        for team in teams:
            for m in team.get("members", []):
                members.append({
                    "id": m["user"]["id"],
                    "username": m["user"]["username"],
                    "email": m["user"]["email"]
                })

            break
        if not members:
            logger.warning("No workspace members found. space_id=%s.", space_id)
            raise ClickUpWorkspaceMembersException(
                f"Workspace '{space_id}' not found or has no members."
            )

        logger.info(
            "%d member(s) retrieved for workspace '%s'.",
            len(members),
            space_id,
        )
        return members

    def _get_folders(self, space_id: str):
        """
        Fetch folders for a space.

        Args:
            space_id: ClickUp space identifier.

        Returns:
            Parsed JSON response of folders.
        """
        logger.info("Fetching folders. space_id=%s.", space_id)

        return self._http.get(f"/space/{space_id}/folder").get("folders", [])

    def _get_lists(self, folder_id: str):
        """
        Fetch lists for a folder.

        Args:
            folder_id: ClickUp folder identifier.

        Returns:
            Parsed JSON response of lists.
        """
        logger.info("Fetching lists. folder_id=%s.", folder_id)

        return self._http.get(f"/folder/{folder_id}/list").get("lists", [])

    def _get_tasks(self, list_id: str):
        """
        Fetch tasks for a list.

        Args:
            list_id: ClickUp list identifier.

        Returns:
            Parsed JSON response of tasks.
        """
        logger.info("Fetching tasks. list_id=%s.", list_id)

        return self._http.get(f"/list/{list_id}/task").get("tasks", [])

    def _get_list_details(self, list_id: str):
        """
        Fetch full list details, including statuses and priorities.

        Args:
            list_id: ClickUp list identifier.

        Returns:
            Parsed JSON response of list details.
        """
        logger.info("Fetching list details. list_id=%s.", list_id)

        return self._http.get(f"/list/{list_id}")
