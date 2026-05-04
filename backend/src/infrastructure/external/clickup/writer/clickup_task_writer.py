"""
ClickUp task writer adapter for applying create/update actions.

This module defines the ClickUpTaskWriter class, which implements the
IClickUpTaskWriter port. It is responsible for applying task creation and update
operations to ClickUp based on verified domain results.

This adapter acts as an infrastructure layer component translating domain-level
task decisions into ClickUp API requests.
"""

import logging
from typing import List

from backend.src.domain.entities.clickup.folder import Folder
from backend.src.domain.entities.verify_tasks.verified_task import VerifiedTask
from backend.src.domain.exceptions.clickup.clickup_task_create_exception import ClickUpTaskCreateException
from backend.src.domain.exceptions.clickup.clickup_task_update_exception import ClickUpTaskUpdateException
from backend.src.domain.ports.output.clickup.i_clickup_writer import IClickUpTaskWriter
from backend.src.infrastructure.external.clickup.client.clickup_http_client import ClickUpHttpClient
from backend.src.infrastructure.external.clickup.helpers.clickup_helper import resolve_assignee_ids_strict, priority_to_int


logger = logging.getLogger(__name__)


class ClickUpTaskWriter(IClickUpTaskWriter):
    """
    ClickUp infrastructure adapter for writing task changes.

    This class centralizes:
    - Creation of ClickUp tasks from verified domain results
    - Updating existing ClickUp tasks based on verification output
    - Mapping domain entities into ClickUp API payloads

    It ensures synchronization between domain decisions and ClickUp workspace state.

    Attributes:
        _http (ClickUpHttpClient): HTTP client used for API communication.
    """

    def __init__(self, http_client: ClickUpHttpClient):
        """Initialize the writer with an HTTP client.

        Args:
            http_client: ClickUp HTTP client instance used for API calls.
        """
        self._http = http_client

    def apply_results(
            self,
            results: List[VerifiedTask],
            folders: List[Folder],
            members: List[dict],
            name_to_email: dict[str, str],
            ignore_mails: bool
    ) -> None:
        """
        Apply verified task results to ClickUp.

        This method processes a list of verified tasks and applies the required
        operations (create or update) in ClickUp by routing them to the correct
        folder and resolving assignees.

        Args:
            results (List[VerifiedTask]): List of verified task operations to apply.
            folders (List[Folder]): ClickUp folder structure used to resolve list identifiers.
            members (List[dict]): Workspace members used for assignee resolution.
            name_to_email (dict[str, str]): Mapping of assignee names to email addresses.
            ignore_mails (bool):
                If True, unresolved assignees are ignored.
                If False, an exception is raised when resolution fails.

        Returns:
            None

        Raises:
            ClickUpTaskCreateException: If task creation fails.
            ClickUpTaskUpdateException: If task update fails.
        """
        logger.info(
            "Starting ClickUp task synchronization. total_results=%d, folders=%d, members=%d.",
            len(results),
            len(folders),
            len(members),
        )

        name_to_email = name_to_email
        email_to_id = {m["email"].lower(): m["id"] for m in members}

        location_list_map = ClickUpTaskWriter._build_location_list_map(folders)

        created_count = 0
        updated_count = 0
        skipped_count = 0

        for result in results:
            if result.action == "create":
                list_id = location_list_map.get(result.location)
                if not list_id:
                    logger.warning(
                        "Create skipped: folder_not_found. location=%s task_name=%s.",
                        result.location,
                        result.task_name,
                    )
                    skipped_count += 1
                    continue

                try:
                    self._create_task(list_id, result, name_to_email, email_to_id, ignore_mails)
                    created_count += 1
                except ClickUpTaskCreateException as e:
                    logger.error(
                        "Create failed: task_name=%s folder=%s error=%s.",
                        result.task_name,
                        result.folder,
                        str(e),
                    )
                    raise

            elif result.action == "update":
                if not result.task_id:
                    logger.warning(
                        "Update requested but no task_id provided for '%s' — skipping.",
                        result.task_name,
                    )
                    skipped_count += 1
                    continue

                try:
                    self._update_task(result, name_to_email, email_to_id, ignore_mails)
                    updated_count += 1
                except ClickUpTaskUpdateException as e:
                    logger.error(
                        "Update failed: task_id=%s task_name=%s error=%s.",
                        result.task_id,
                        result.task_name,
                        str(e),
                    )
                    raise

        logger.info(
            "ClickUp synchronization completed. created=%d updated=%d skipped=%d total=%d.",
            created_count,
            updated_count,
            skipped_count,
            len(results),
        )

    def _create_task(
            self,
            list_id: str,
            result: VerifiedTask,
            name_to_email: dict[str, str],
            email_to_id: dict[str, int],
            ignore_mails: bool
    ) -> None:
        """
        Create a task in ClickUp.

        This method builds a ClickUp task payload from a verified domain task
        and sends a creation request to the ClickUp API.

        Args:
            list_id: ClickUp list identifier where the task will be created.
            result: Verified task containing creation details.
            name_to_email: Mapping of usernames to emails for resolution.
            email_to_id: Mapping of emails to ClickUp member IDs.
            ignore_mails (bool):
                If True, unresolved assignees are ignored.
                If False, an exception is raised when resolution fails.

        Returns:
            None.

        Raises:
            ClickUpTaskCreateException: If the API request fails.
        """
        logger.info(
            "Creating ClickUp task. task_name=%s location=%s list_id=%s.",
            result.task_name,
            result.location,
            list_id,
        )

        endpoint = f"/list/{list_id}/task"

        payload = {
            "name": result.task_name,
            "description": result.task_description,
            "status": result.task_status,
            "priority": priority_to_int(result.task_priority),
        }

        assignee_names = [a.strip() for a in result.task_assigne.split(",")]
        assignee_ids = resolve_assignee_ids_strict(name_to_email, email_to_id, assignee_names, ignore_mails)

        if assignee_ids:
            payload["assignees"] = assignee_ids

        response = self._http.post_raw(endpoint, payload)

        if response.status_code == 200:
            logger.info(
                "Task created successfully. task_name=%s location=%s status_code=%d.",
                result.task_name,
                result.location,
                response.status_code,
            )
        else:
            logger.error(
                "Task creation failed. task_name=%s location=%s status_code=%d response=%s.",
                result.task_name,
                result.location,
                response.status_code,
                response.text,
            )
            raise ClickUpTaskCreateException(
                f"Failed to create '{result.task_name}' "
                f"(status {response.status_code}) — {response.text}"
            )

    def _update_task(
            self,
            result: VerifiedTask,
            name_to_email: dict[str, str],
            email_to_id: dict[str, int],
            ignore_mails: bool
    ) -> None:
        """
        Update an existing task in ClickUp.

        This method updates task status, priority, and assignees in ClickUp
        based on the verified domain result.

        Args:
            result: Verified task containing update information.
            name_to_email: Mapping of usernames to emails for resolution.
            email_to_id: Mapping of emails to ClickUp member IDs.
            ignore_mails (bool):
                If True, unresolved assignees are ignored.
                If False, an exception is raised when resolution fails.

        Returns:
            None.

        Raises:
            ClickUpTaskUpdateException: If the API request fails.
        """
        logger.info(
            "Updating ClickUp task. task_id=%s task_name=%s.",
            result.task_id,
            result.task_name,
        )

        endpoint = f"/task/{result.task_id}"

        payload = {
            "status": result.task_status,
            "priority": priority_to_int(result.task_priority),
        }

        assignee_names = [a.strip() for a in result.task_assigne.split(",")]
        assignee_ids = resolve_assignee_ids_strict(name_to_email, email_to_id, assignee_names, ignore_mails)
        if assignee_ids:
            payload["assignees"] = {"add": assignee_ids}

        response = self._http.put_raw(endpoint, payload)

        if response.status_code == 200:
            logger.info(
                "Task updated successfully. task_id=%s task_name=%s status_code=%d.",
                result.task_id,
                result.task_name,
                response.status_code,
            )
        else:
            logger.error(
                "Task update failed. task_id=%s task_name=%s status_code=%d response=%s.",
                result.task_id,
                result.task_name,
                response.status_code,
                response.text,
            )
            raise ClickUpTaskUpdateException(
                f"Failed to update '{result.task_name}' id='{result.task_id}' "
                f"(status {response.status_code}) — {response.text}"
            )

    @staticmethod
    def _build_location_list_map(folders: List[Folder]) -> dict:
        """
        Build a mapping of location label to list ID.

        Location label format:
        - "FolderName / ListName" for lists inside a folder
        - "ListName" for folderless lists (folder.id == lst.id)

        Args:
            folders: Folder objects with lists.

        Returns:
            Mapping of location label to list ID.
        """
        mapping = {}
        for folder in folders:
            for lst in folder.lists:
                label = lst.name if folder.id == lst.id else f"{folder.name} / {lst.name}"
                mapping[label] = lst.id
        return mapping