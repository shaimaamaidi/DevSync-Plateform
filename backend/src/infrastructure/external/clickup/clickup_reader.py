"""
ClickUp reader adapter for retrieving workspace structure and members.

This module defines the ClickUpReader class, which implements the IClickUpReader
port. It is responsible for fetching ClickUp space structure (folders, lists,
tasks) and workspace members using the ClickUp HTTP client.

This adapter acts as an infrastructure layer component translating ClickUp API
responses into domain entities.
"""

import logging
from typing import List, Optional

from backend.src.domain.entities.clickup.list import ClickUpList, ClickUpTask
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

        Includes folders, lists, and tasks mapped into domain entities.

        Args:
            space_id: ClickUp space identifier.

        Returns:
            List of Folder objects containing lists, tasks, statuses, and priorities.

        Raises:
            ClickUpEmptySpaceException: If the space has no folders.
        """
        logger.info("Fetching space structure. space_id=%s.", space_id)

        folders_data = self._get_folders(space_id)
        folderless_lists_data = self._get_folderless_lists(space_id)

        if not folders_data and not folderless_lists_data:
            logger.warning("Empty ClickUp space. space_id=%s.", space_id)
            raise ClickUpEmptySpaceException(
                f"No folder found in space '{space_id}'."
            )

        folders: List[Folder] = []

        if folders_data:
            logger.info(
                "%d folder(s) found directly in space '%s'.",
                len(folders_data),
                space_id,
            )
            for folder_data in folders_data:
                folder = self._build_folder(folder_data)
                folders.append(folder)

        if folderless_lists_data:
            logger.info(
                "%d folderless list(s) found directly in space '%s'.",
                len(folderless_lists_data),
                space_id,
            )
            for list_data in folderless_lists_data:
                clickup_list = self._build_list(list_data)
                folders.append(
                    Folder(
                        id=list_data["id"],
                        name="__folderless__",
                        lists=[clickup_list],
                    )
                )

        logger.info(
            "Space structure completed. space_id=%s folders=%d.",
            space_id,
            len(folders),
        )

        return folders

    def get_workspace_members(self, space_id: str) -> List[dict]:
        """
        Retrieve ClickUp workspace members from the first available team.

        Only the first team is used — in most ClickUp configurations a single
        workspace maps to a single team.

        Args:
            space_id: ClickUp space identifier (used for logging context only).

        Returns:
            List of member dicts with keys: id, username, email.

        Raises:
            ClickUpWorkspaceMembersException: If no valid members are found.
        """
        logger.info("Fetching workspace members. space_id=%s.", space_id)

        teams = self._http.get("/team").get("teams", [])

        members = []

        if teams:
            first_team = teams[0]
            for m in first_team.get("members", []):
                parsed = self._parse_member(m)
                if parsed:
                    members.append(parsed)
                else:
                    logger.warning(
                        "Skipping incomplete member entry. entry=%s.", m
                    )

        if not members:
            logger.warning("No valid workspace members found. space_id=%s.", space_id)
            raise ClickUpWorkspaceMembersException(
                f"Workspace '{space_id}' not found or has no members."
            )

        logger.info(
            "%d member(s) retrieved. space_id=%s.",
            len(members),
            space_id,
        )

        return members

    def _build_folder(self, folder_data: dict) -> Folder:
        """
        Build a Folder domain entity from a raw API folder dict.

        Args:
            folder_data: Raw folder dictionary from ClickUp API.

        Returns:
            Folder domain entity.
        """
        folder_id = folder_data.get("id", "<unknown>")
        folder_name = folder_data.get("name", "<unknown>")

        logger.info("Processing folder '%s'. folder_id=%s.", folder_name, folder_id)

        lists_data = self._get_lists(folder_id)

        lists = [self._build_list(list_data) for list_data in lists_data]

        return Folder(id=folder_id, name=folder_name, lists=lists)

    def _build_list(self, list_data: dict) -> ClickUpList:
        """
        Build a ClickUpList domain entity from a raw API list dict.

        Args:
            list_data: Raw list dictionary from ClickUp API.

        Returns:
            ClickUpList domain entity.
        """
        list_id = list_data.get("id", "<unknown>")
        list_name = list_data.get("name", "<unknown>")

        list_details = self._get_list_details(list_id)
        tasks_data = self._get_tasks(list_id)

        tasks = [self._parse_task(task) for task in tasks_data]

        statuses = [
            s["status"]
            for s in list_details.get("statuses", [])
            if s.get("status")
        ]

        logger.info(
            "List '%s' built. list_id=%s tasks=%d statuses=%d.",
            list_name,
            list_id,
            len(tasks),
            len(statuses),
        )

        return ClickUpList(
            id=list_id,
            name=list_name,
            tasks=tasks,
            statuses=statuses,
            priorities=PRIORITIES,
        )

    @staticmethod
    def _parse_task(task: dict) -> ClickUpTask:
        """
        Build a ClickUpTask domain entity from a raw API task dict.

        Uses safe .get() access on every field to prevent KeyError
        when the API response has an unexpected or incomplete structure.

        Args:
            task: Raw task dictionary from ClickUp API.

        Returns:
            ClickUpTask domain entity.
        """
        assignees = task.get("assignees") or []
        assignee: Optional[str] = (
            assignees[0].get("username") if assignees else None
        )

        status_field = task.get("status") or {}
        status: str = status_field.get("status", "")

        priority_field = task.get("priority") or {}
        priority: Optional[str] = priority_field.get("priority")

        return ClickUpTask(
            id=task.get("id", ""),
            name=task.get("name", ""),
            description=task.get("description", ""),
            status=status,
            assignee=assignee,
            priority=priority,
        )

    @staticmethod
    def _parse_member(member: dict) -> Optional[dict]:
        """
        Extract and validate a member dict from a raw API member entry.

        Returns None if any required field (id, username, email) is missing,
        so the caller can skip and log incomplete entries without raising.

        Args:
            member: Raw member dictionary from ClickUp API.

        Returns:
            Validated member dict with keys id, username, email — or None.
        """
        user = member.get("user") or {}
        user_id = user.get("id")
        username = user.get("username")
        email = user.get("email")

        if not (user_id and username and email):
            return None

        return {"id": user_id, "username": username, "email": email}

    def _get_folders(self, space_id: str) -> list:
        """
        Fetch folders for a space.

        Args:
            space_id: ClickUp space identifier.

        Returns:
            List of folder dicts from the API response.
        """
        logger.info("Fetching folders. space_id=%s.", space_id)
        return self._http.get(f"/space/{space_id}/folder").get("folders", [])

    def _get_lists(self, folder_id: str) -> list:
        """
        Fetch lists for a folder.

        Args:
            folder_id: ClickUp folder identifier.

        Returns:
            List of list dicts from the API response.
        """
        logger.info("Fetching lists. folder_id=%s.", folder_id)
        return self._http.get(f"/folder/{folder_id}/list").get("lists", [])

    def _get_tasks(self, list_id: str) -> list:
        """
        Fetch tasks for a list.

        Args:
            list_id: ClickUp list identifier.

        Returns:
            List of task dicts from the API response.
        """
        logger.info("Fetching tasks. list_id=%s.", list_id)
        return self._http.get(f"/list/{list_id}/task").get("tasks", [])

    def _get_list_details(self, list_id: str) -> dict:
        """
        Fetch full list details, including statuses.

        Args:
            list_id: ClickUp list identifier.

        Returns:
            Parsed JSON dict of list details.
        """
        logger.info("Fetching list details. list_id=%s.", list_id)
        return self._http.get(f"/list/{list_id}")

    def _get_folderless_lists(self, space_id: str):
        """Fetch lists that sit directly in a space (not inside any folder).

        Args:
            space_id: ClickUp space identifier.

        Returns:
            Parsed JSON response of folderless lists.
        """
        return self._http.get(f"/space/{space_id}/list").get("lists", [])