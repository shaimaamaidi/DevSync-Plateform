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

from backend.src.domain.entities.clickup.folder_with_list_metadata import FolderWithListsMetadata
from backend.src.domain.entities.clickup.list_metadata import ClickUpListMetadata
from backend.src.domain.entities.clickup.list_with_tasks import ClickUpList
from backend.src.domain.entities.clickup.folder_with_lists import FolderWithLists
from backend.src.domain.exceptions.clickup.clickup_client_exception import ClickUpClientException
from backend.src.domain.exceptions.clickup.clickup_resource_not_found_exception import ClickUpResourceNotFoundException
from backend.src.domain.exceptions.clickup.clickup_workspace_members_exception import ClickUpWorkspaceMembersException
from backend.src.domain.ports.output.clickup.i_clickup_reader import IClickUpReader
from backend.src.infrastructure.external.clickup.client.clickup_http_client import ClickUpHttpClient
from backend.src.infrastructure.external.clickup.helpers.clickup_helper import parse_task

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

    def space_exists(self, space_code: str) -> str:
        """
        Check whether a ClickUp space exists and is accessible.

        Args:
            space_code: ClickUp space identifier in the click up.

        Returns:
            Space name if the space exists and is accessible.

        Raises:
            ClickUpResourceNotFoundException: When a space is not found.
        """
        logger.info("Checking space existence. space_code=%s.", space_code)

        try:
            response = self._http.get(f"/space/{space_code}")

            space_name = response.get("name", "")
        except ClickUpClientException as e:
            raise ClickUpResourceNotFoundException(
                f"Space not found: {space_code}"
            ) from e

        logger.info("Space found. space_code=%s, name=%s.", space_code, space_name)

        return space_name

    def get_space_full_structure(self, space_id: str) -> List[FolderWithLists]:
        """
        Retrieve full ClickUp space structure.

        Includes folders, lists, and tasks mapped into domain entities.

        Args:
            space_id: ClickUp space identifier.

        Returns:
            List of Folder objects containing lists, tasks, statuses, and priorities.
        """
        logger.info("Fetching space structure. space_id=%s.", space_id)

        folders_data = self._get_folders(space_id)
        folderless_lists_data = self._get_folderless_lists(space_id)

        if not folders_data and not folderless_lists_data:
            logger.warning("Empty ClickUp space. space_id=%s.", space_id)
            return []

        folders: List[FolderWithLists] = []

        if folders_data:
            logger.info(
                "%d folder(s) found directly in space '%s'.",
                len(folders_data),
                space_id,
            )
            for folder_data in folders_data:
                folder = self._build_folder_with_lists(folder_data)
                folders.append(folder)

        if folderless_lists_data:
            logger.info(
                "%d folderless list(s) found directly in space '%s'.",
                len(folderless_lists_data),
                space_id,
            )
            for list_data in folderless_lists_data:
                clickup_list = self._build_list_with_tasks(list_data)
                folders.append(
                    FolderWithLists(
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

    def get_space_structure_metadata(self, space_id: str) -> List[FolderWithListsMetadata]:
        """
        Retrieve ClickUp space structure (metadata only).

        Includes folders and lists with their configuration metadata
        (statuses and priorities), without retrieving tasks.

        Args:
            space_id: ClickUp space identifier.

        Returns:
            List of FolderWithListsMetadata containing lists metadata.
        """
        logger.info("Fetching space structure. space_id=%s.", space_id)

        folders_data = self._get_folders(space_id)
        folderless_lists_data = self._get_folderless_lists(space_id)

        if not folders_data and not folderless_lists_data:
            logger.warning("Empty ClickUp space. space_id=%s.", space_id)
            return []

        folders: List[FolderWithListsMetadata] = []

        if folders_data:
            logger.info(
                "%d folder(s) found directly in space '%s'.",
                len(folders_data),
                space_id,
            )
            for folder_data in folders_data:
                folder = self._build_folder_with_metadata(folder_data)
                folders.append(folder)

        if folderless_lists_data:
            logger.info(
                "%d folderless list(s) found directly in space '%s'.",
                len(folderless_lists_data),
                space_id,
            )
            for list_data in folderless_lists_data:
                clickup_list = self._build_list_with_metadata(list_data)
                folders.append(
                    FolderWithListsMetadata(
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

    def get_workspace_members(self) -> List[dict]:
        """
        Retrieve ClickUp workspace members from the first available team.

        Only the first team is used — in most ClickUp configurations a single
        workspace maps to a single team.

        Returns:
            List of member dicts with keys: id, username, email.
        """
        logger.info("Fetching workspace members.")

        ASSIGNABLE_ROLES = {20, 40, 60}

        teams = self._http.get("/team").get("teams", [])

        members = []

        for team in teams:
            for m in team.get("members", []):
                role_code = (m.get("user") or {}).get("role")
                if role_code not in ASSIGNABLE_ROLES:
                    logger.warning(
                        "Skipping non-assignable member (role=%s). entry=%s.", role_code, m
                    )
                    continue

                parsed = self._parse_member(m)
                if parsed:
                    members.append(parsed)
                else:
                    logger.warning(
                        "Skipping incomplete member entry. entry=%s.", m
                    )

        if not members:
            logger.warning("No valid workspace members found.")
            return []

        logger.info(
            "%d member(s) retrieved.",
            len(members),
        )

        return members

    def get_workspace_members_with_roles(self) -> List[dict]:
        """
        Retrieve ClickUp workspace members with their roles from the first available team.

        Returns:
            List of member dicts with keys: id, email, role.

        Raises:
            ClickUpWorkspaceMembersException: If no valid members are found.
        """
        logger.info("Fetching workspace members with roles.")

        teams = self._http.get("/team").get("teams", [])

        members = []

        for team in teams:
            for m in team.get("members", []):
                parsed = self._parse_member_with_role(m)
                if parsed:
                    members.append(parsed)
                else:
                    logger.warning(
                        "Skipping incomplete member entry. entry=%s.", m
                    )

        if not members:
            logger.warning("No valid workspace members found.")
            raise ClickUpWorkspaceMembersException(
                f"Workspace not found or has no members."
            )

        logger.info(
            "%d member(s) with roles retrieved.",
            len(members),
        )

        return members

    @staticmethod
    def _parse_member_with_role(member: dict) -> Optional[dict]:
        """
        Extract and validate a member dict including their role from a raw API member entry.

        ClickUp role values:
            20 → owner
            40 → admin
            60 → member
            80 → guest

        Returns None if any required field (id, email, role) is missing.

        Args:
            member: Raw member dictionary from ClickUp API.

        Returns:
            Validated member dict with keys id, email, role — or None.
        """
        ROLE_MAP = {
            20: "owner",
            40: "admin",
            60: "member",
            80: "guest",
        }

        user = member.get("user") or {}
        user_id = user.get("id")
        email = user.get("email")
        role_code = user.get("role")

        if not (user_id and email and role_code is not None):
            return None

        role = ROLE_MAP.get(role_code, f"unknown({role_code})")

        return {"id": user_id, "email": email, "role": role}

    def _build_folder_with_lists(self, folder_data: dict) -> FolderWithLists:
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

        lists = [self._build_list_with_tasks(list_data) for list_data in lists_data]

        return FolderWithLists(id=folder_id, name=folder_name, lists=lists)

    def _build_folder_with_metadata(self, folder_data: dict) -> FolderWithListsMetadata:
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

        lists = [self._build_list_with_metadata(list_data) for list_data in lists_data]

        return FolderWithListsMetadata(id=folder_id, name=folder_name, lists=lists)

    def _build_list_with_tasks(self, list_data: dict) -> ClickUpList:
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

        tasks = [parse_task(task) for task in tasks_data]

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

    def _build_list_with_metadata(self, list_data: dict) -> ClickUpListMetadata:
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
        override = list_details.get("override_statuses", False)
        statuses = [
            s["status"]
            for s in list_details.get("statuses", [])
            if s.get("status")
        ]if override else []

        logger.info(
            "List '%s' built. list_id=%s statuses=%d.",
            list_name,
            list_id,
            len(statuses),
        )

        return ClickUpListMetadata(
            id=list_id,
            name=list_name,
            statuses=statuses,
            priorities=PRIORITIES,
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

         Raises:
             ClickUpResourceNotFoundException: When a space is not found.
        """
        logger.info("Fetching folders. space_id=%s.", space_id)

        try:
            results = self._http.get(f"/space/{space_id}/folder").get("folders", [])
        except ClickUpClientException as e:
            raise ClickUpResourceNotFoundException(
                f"Space not found: {space_id}"
            ) from e

        return results

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

        return  self._http.get(f"/list/{list_id}/task").get("tasks", [])

    def _get_list_details(self, list_id: str) -> dict:
        """
        Fetch full list details, including statuses.

        Args:
            list_id: ClickUp list identifier.

        Returns:
            Parsed JSON dict of list details.
        """
        logger.info("Fetching list details. list_id=%s.", list_id)

        return self._http.get(f"/list/{list_id}?override_statuses=true")

    def _get_folderless_lists(self, space_id: str):
        """Fetch lists that sit directly in a space (not inside any folder).

        Args:
            space_id: ClickUp space identifier.

        Returns:
            Parsed JSON response of folderless lists.

        Raises:
            ClickUpResourceNotFoundException: When a space is not found.
        """

        try:
            results = self._http.get(f"/space/{space_id}/list").get("lists", [])
        except ClickUpClientException as e:
            raise ClickUpResourceNotFoundException(
                f"Space not found: {space_id}"
            ) from e

        return results