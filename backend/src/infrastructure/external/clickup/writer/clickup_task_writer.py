"""
ClickUp task writer adapter for applying task create, update, and delete operations.

This module defines the ClickUpTaskWriter class, an infrastructure adapter
responsible for synchronizing verified task operations with ClickUp.

The adapter translates domain-level task actions into ClickUp API requests and
handles:
- Task creation
- Task updates
- Task deletion
- Assignee resolution
- Folder/list mapping resolution

It ensures consistency between verified domain decisions and the remote
ClickUp workspace state while providing centralized logging and error handling
for task write operations.
"""

import logging
from typing import List

from backend.src.domain.entities.clickup.folder_with_list_metadata import FolderWithListsMetadata
from backend.src.domain.entities.clickup.list_with_tasks import ClickUpTask
from backend.src.domain.entities.verified_tasks.verified_task_from_backlog import VerifiedTaskFromBacklog
from backend.src.domain.entities.verified_tasks.verified_task_from_summary import VerifiedTaskFromSummary
from backend.src.domain.exceptions.clickup.clickup_task_create_exception import ClickUpTaskCreateException
from backend.src.domain.exceptions.clickup.clickup_task_delete_exception import ClickUpTaskDeleteException
from backend.src.domain.exceptions.clickup.clickup_task_update_exception import ClickUpTaskUpdateException
from backend.src.domain.ports.output.clickup.i_clickup_task_writer import IClickUpTaskWriter
from backend.src.infrastructure.external.clickup.client.clickup_http_client import ClickUpHttpClient
from backend.src.infrastructure.external.clickup.helpers.clickup_helper import resolve_assignee_ids_strict, \
    priority_to_str, resolve_assignee_ids_from_mails, parse_task

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

    def create_task_by_list(
        self,
        list_id: str,
        task: ClickUpTask,
        email_to_id: dict[str, int],
        ignore_mails:bool
    ) -> ClickUpTask:
        """
        Create a task directly in a ClickUp list.

        This method builds a ClickUp task payload from a Task entity and sends
        a creation request to the ClickUp API. Assignee emails are resolved into
        ClickUp member IDs before the request is sent.

        Args:
            list_id: Identifier of the ClickUp list where the task will be created.
            task: Task entity containing task details.
            email_to_id: Mapping of user emails to ClickUp member IDs.
            ignore_mails:
                If True, unresolved assignee emails are ignored.
                If False, an exception is raised for unresolved emails.

        Returns:
            ClickUpTask: created task.

        Raises:
            ClickUpTaskCreateException: Raised when the ClickUp API task creation request fails.
        """
        logger.info(
            "Creating ClickUp task. task_name=%s list_id=%s.",
            task.name,
            list_id,
        )

        endpoint = f"/list/{list_id}/task"

        payload = {
            "name": task.name,
            "description": task.description,
        }

        priority = priority_to_str(task.priority)
        if priority is not None:
            payload["priority"] = priority

        if task.status:
            payload["status"] = task.status

        assignee_ids = []

        if task.assignee:
            assignee_mails = [a.strip() for a in task.assignee.split(",")]
            assignee_ids = resolve_assignee_ids_from_mails(email_to_id, assignee_mails, ignore_mails)

        if assignee_ids:
            payload["assignees"] = assignee_ids

        response = self._http.post_raw(endpoint, payload)

        if response.status_code == 200:
            logger.info(
                "Task created successfully. task_name=%s task_status=%s status_code=%d.",
                task.name,
                task.status,
                response.status_code,
            )
            return parse_task(response.json())
        else:
            logger.error(
                "Task creation failed. task_name=%s status_code=%d response=%s.",
                task.name,
                response.status_code,
                response.text,
            )
            raise ClickUpTaskCreateException(
                f"The task \"{task.name}\" could not be created in ClickUp. Please try again or contact support."
            )

    def update_task(
        self,
        task_id: str,
        task_content: ClickUpTask,
        old_assignees: str,
        email_to_id: dict[str, int],
        ignore_mails: bool
    ) -> ClickUpTask:
        """
        Update an existing ClickUp task.

        This method updates task status, priority, and assignees in ClickUp.
        It compares existing assignees with the new assignees to determine
        which assignees should be added or removed.

        Args:
            task_id: Identifier of the ClickUp task to update.
            task_content: Updated task content and metadata.
            old_assignees: Comma-separated list of previous assignee emails.
            email_to_id: Mapping of user emails to ClickUp member IDs.
            ignore_mails:
                If True, unresolved assignee emails are ignored.
                If False, an exception is raised for unresolved emails.

        Returns:
            ClickUpTask: updated task.

        Raises:
            ClickUpTaskUpdateException:
                Raised when the ClickUp API update request fails.
        """
        logger.info(
            "Updating ClickUp task. task_id=%s task_name=%s.",
            task_id,
            task_content.name,
        )

        endpoint = f"/task/{task_id}"

        payload = {
            "name": task_content.name,
            "description": task_content.description,
        }

        priority = priority_to_str(task_content.priority)
        if priority is not None:
            payload["priority"] = priority

        if task_content.status:
            payload["status"] = task_content.status

        added_ids = []
        rem_ids = []

        if task_content.assignee or old_assignees:
            new_assignee_mails = [a.strip() for a in task_content.assignee.split(",") if a.strip()]
            old_assignee_mails = [a.strip() for a in old_assignees.split(",") if a.strip()] if old_assignees else []

            new_assignee_ids = resolve_assignee_ids_from_mails(email_to_id, new_assignee_mails, ignore_mails) if new_assignee_mails else []
            old_assignee_ids = resolve_assignee_ids_from_mails(email_to_id, old_assignee_mails, ignore_mails) if old_assignee_mails else []

            added_ids = list(set(new_assignee_ids) - set(old_assignee_ids))
            rem_ids = list(set(old_assignee_ids) - set(new_assignee_ids))

        if added_ids or rem_ids:
            payload["assignees"] = {}
            if added_ids:
                payload["assignees"]["add"] = added_ids
            if rem_ids:
                payload["assignees"]["rem"] = rem_ids

        response = self._http.put_raw(endpoint, payload)

        if response.status_code == 200:
            logger.info(
                "Task updated successfully. task_id=%s task_name=%s status_code=%d.",
                task_id,
                task_content.name,
                response.status_code,
            )
            return parse_task(response.json())
        else:
            logger.error(
                "Task update failed. task_id=%s task_name=%s status_code=%d response=%s.",
                task_id,
                task_content.name,
                response.status_code,
                response.text,
            )
            raise ClickUpTaskUpdateException(
                f"The task \"{task_content.name}\" could not be updated in ClickUp. Please try again or contact support."
            )

    def delete_task(self, task_id: str) -> bool:
        """
        Delete a task from ClickUp.

        This method sends a deletion request to the ClickUp API for the
        specified task identifier.

        Args:
            task_id: Identifier of the ClickUp task to delete.

        Returns:
            bool: True if deletion was successful.

        Raises:
            ClickUpTaskDeleteException:
                Raised when the ClickUp API deletion request fails.
        """
        logger.info("Deleting task. task_id=%s.", task_id)

        endpoint = f"/task/{task_id}"
        response = self._http.delete_raw(endpoint)

        if response.status_code in (200, 204):
            logger.info("Task deleted successfully. task_id=%s.", task_id)
            return True

        logger.error(
            "Task deletion failed. task_id=%s status_code=%d response=%s.",
            task_id,
            response.status_code,
            response.text,
        )
        raise ClickUpTaskDeleteException(
            "The task could not be deleted from ClickUp. Please try again or contact support."
        )

    def apply_summary_results(
            self,
            results: List[VerifiedTaskFromSummary],
            folders: List[FolderWithListsMetadata],
            members: List[dict],
            name_to_email: dict[str, str],
            ignore_names: bool,
            ignore_mails: bool
    ) -> None:
        """
        Apply verified summary task results to ClickUp.

        This method processes a list of verified summary tasks and applies the required
        operations (create or update) in ClickUp by routing them to the correct
        folder and resolving assignees.

        Args:
            results (List[VerifiedTaskFromSummary]): List of verified task operations to apply.
            folders (List[FolderWithListsMetadata]): ClickUp folder structure used to resolve list identifiers.
            members (List[dict]): Workspace members used for assignee resolution.
            name_to_email (dict[str, str]): Mapping of assignee names to email addresses.
            ignore_names (bool):
                If True, names without an email mapping are ignored.
                If False, an exception is raised for unresolved names.
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
            "Starting summary task synchronization. total_results=%d, folders=%d, members=%d.",
            len(results),
            len(folders),
            len(members),
        )

        created_count, updated_count, skipped_count =ClickUpTaskWriter._apply_results(
            results, folders, members, name_to_email, ignore_names, ignore_mails,
            create_fn=self._create_summary_task,
            update_fn=self._update_summary_task,
        )

        logger.info(
            "ClickUp synchronization completed. created=%d updated=%d skipped=%d total=%d.",
            created_count,
            updated_count,
            skipped_count,
            len(results),
        )

    def apply_backlog_results(
            self,
            results: List[VerifiedTaskFromBacklog],
            folders: List[FolderWithListsMetadata],
            members: List[dict],
            name_to_email: dict[str, str],
            ignore_names: bool,
            ignore_mails: bool
    ) -> None:
        """
        Apply verified backlog task results to ClickUp.

        This method processes a list of verified backlog tasks and applies the required
        operations (create or update) in ClickUp by routing them to the correct
        folder and resolving assignees.

        Args:
            results (List[VerifiedTaskFromSummary]): List of verified task operations to apply.
            folders (List[FolderWithListsMetadata]): ClickUp folder structure used to resolve list identifiers.
            members (List[dict]): Workspace members used for assignee resolution.
            name_to_email (dict[str, str]): Mapping of assignee names to email addresses.
            ignore_names (bool):
                If True, names without an email mapping are ignored.
                If False, an exception is raised for unresolved names.
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
            "Starting backlog task synchronization. total_results=%d, folders=%d, members=%d.",
            len(results),
            len(folders),
            len(members),
        )

        created_count, updated_count, skipped_count = ClickUpTaskWriter._apply_results(
            results, folders, members, name_to_email, ignore_names, ignore_mails,
            create_fn=self._create_backlog_task,
            update_fn=self._update_backlog_task,
        )

        logger.info(
            "ClickUp synchronization completed. created=%d updated=%d skipped=%d total=%d.",
            created_count,
            updated_count,
            skipped_count,
            len(results),
        )

    @staticmethod
    def _apply_results(
        results: List,
        folders: List[FolderWithListsMetadata],
        members: List[dict],
        name_to_email: dict[str, str],
        ignore_names: bool,
        ignore_mails: bool,
        create_fn,
        update_fn,
    ) -> tuple[int, int, int]:
        """
        Apply verified task results to ClickUp.

        This method processes a list of verified tasks and applies the required
        operations (create or update) in ClickUp by routing them to the correct
        folder and resolving assignees.

        Args:
            results (List): List of verified task operations to apply.
            folders (List[FolderWithListsMetadata]): ClickUp folder structure used to resolve list identifiers.
            members (List[dict]): Workspace members used for assignee resolution.
            name_to_email (dict[str, str]): Mapping of assignee names to email addresses.
            ignore_names (bool):
                If True, names without an email mapping are ignored.
                If False, an exception is raised for unresolved names.
            ignore_mails (bool):
                If True, unresolved assignees are ignored.
                If False, an exception is raised when resolution fails.

        Returns:
            tuple[int, int, int] : created_count, updated_count, skipped_count

        Raises:
            ClickUpTaskCreateException: If task creation fails.
            ClickUpTaskUpdateException: If task update fails.
        """
        email_to_id = {}

        created_count = 0
        updated_count = 0
        skipped_count = 0

        if members:
            email_to_id = {m["email"].lower(): m["id"] for m in members}

        location_list_map = ClickUpTaskWriter._build_location_list_map(folders)

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
                    create_fn(list_id, result, name_to_email, email_to_id, ignore_names, ignore_mails)
                    created_count += 1
                except ClickUpTaskCreateException as e:
                    logger.error(
                        "Create failed: task_name=%s location=%s error=%s.",
                        result.task_name,
                        result.location,
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
                    update_fn(result, name_to_email, email_to_id, ignore_names, ignore_mails)
                    updated_count += 1
                except ClickUpTaskUpdateException as e:
                    logger.error(
                        "Update failed: task_id=%s task_name=%s error=%s.",
                        result.task_id,
                        result.task_name,
                        str(e),
                    )
                    raise
        return created_count, updated_count, skipped_count

    def _create_summary_task(
            self,
            list_id: str,
            result: VerifiedTaskFromSummary,
            name_to_email: dict[str, str],
            email_to_id: dict[str, int],
            ignore_names: bool,
            ignore_mails: bool
    ) -> None:
        """
        Create a summary task in ClickUp.

        This method builds a ClickUp task payload from a verified summary task
        and sends a creation request to the ClickUp API.

        Args:
            list_id: ClickUp list identifier where the task will be created.
            result: Verified summary task containing creation details.
            name_to_email: Mapping of usernames to emails for resolution.
            email_to_id: Mapping of emails to ClickUp member IDs.
            ignore_names (bool):
                If True, names without an email mapping are ignored.
                If False, an exception is raised for unresolved names.
            ignore_mails (bool):
                If True, unresolved assignees are ignored.
                If False, an exception is raised when resolution fails.

        Returns:
            None.

        Raises:
            ClickUpTaskCreateException: If the API request fails.
        """
        logger.info(
            "Creating summary task. task_name=%s location=%s list_id=%s.",
            result.task_name,
            result.location,
            list_id,
        )

        endpoint = f"/list/{list_id}/task"

        payload = ClickUpTaskWriter._build_task_payload(result, include_name=True)

        assignee_ids = ClickUpTaskWriter._resolve_assignee_ids(result, name_to_email, email_to_id, ignore_names,ignore_mails)

        if assignee_ids:
            payload["assignees"] = assignee_ids

        self._post_task(endpoint, payload, task_name=result.task_name, location=result.location, task_status=result.task_status)

    def _create_backlog_task(
            self,
            list_id: str,
            result: VerifiedTaskFromBacklog,
            name_to_email: dict[str, str],
            email_to_id: dict[str, int],
            ignore_names: bool,
            ignore_mails: bool
    ) -> None:
        """
        Create a backlog task in ClickUp.

        This method builds a ClickUp task payload from a verified backlog task
        and sends a creation request to the ClickUp API.

        Args:
            list_id: ClickUp list identifier where the task will be created.
            result: Verified backlog task containing creation details.
            name_to_email: Mapping of usernames to emails for resolution.
            email_to_id: Mapping of emails to ClickUp member IDs.
            ignore_names (bool):
                If True, names without an email mapping are ignored.
                If False, an exception is raised for unresolved names.
            ignore_mails (bool):
                If True, unresolved assignees are ignored.
                If False, an exception is raised when resolution fails.

        Returns:
            None.

        Raises:
            ClickUpTaskCreateException: If the API request fails.
        """
        logger.info(
            "Creating backlog task. task_name=%s location=%s list_id=%s.",
            result.task_name,
            result.location,
            list_id,
        )

        endpoint = f"/list/{list_id}/task"

        payload = ClickUpTaskWriter._build_task_payload(result, include_name=True)

        if result.estimation is not None:
            payload["time_estimate"] = result.estimation * 3_600_000

        assignee_ids = ClickUpTaskWriter._resolve_assignee_ids(result, name_to_email, email_to_id, ignore_names,ignore_mails)

        if assignee_ids:
            payload["assignees"] = assignee_ids

        self._post_task(endpoint, payload, task_name=result.task_name, location=result.location, task_status=result.task_status)

    def _update_summary_task(
            self,
            result: VerifiedTaskFromSummary,
            name_to_email: dict[str, str],
            email_to_id: dict[str, int],
            ignore_names: bool,
            ignore_mails: bool
    ) -> None:
        """
        Update an existing summary task in ClickUp.

        This method updates summary task status, priority, and assignees in ClickUp
        based on the verified domain result.

        Args:
            result: Verified summary task containing update information.
            name_to_email: Mapping of usernames to emails for resolution.
            email_to_id: Mapping of emails to ClickUp member IDs.
            ignore_names (bool):
                If True, names without an email mapping are ignored.
                If False, an exception is raised for unresolved names.
            ignore_mails (bool):
                If True, unresolved assignees are ignored.
                If False, an exception is raised when resolution fails.

        Returns:
            None.

        Raises:
            ClickUpTaskUpdateException: If the API request fails.
        """
        logger.info(
            "Updating summary task. task_id=%s task_name=%s.",
            result.task_id,
            result.task_name,
        )

        endpoint = f"/task/{result.task_id}"

        payload = ClickUpTaskWriter._build_task_payload(result, include_name=False)

        assignee_ids = ClickUpTaskWriter._resolve_assignee_ids(result, name_to_email, email_to_id, ignore_names,ignore_mails)

        if assignee_ids:
            payload["assignees"] = {"add": assignee_ids}

        self._put_task(endpoint, payload, task_id=result.task_id, task_name=result.task_name)

    def _update_backlog_task(
            self,
            result: VerifiedTaskFromBacklog,
            name_to_email: dict[str, str],
            email_to_id: dict[str, int],
            ignore_names: bool,
            ignore_mails: bool
    ) -> None:
        """
        Update an existing backlog task in ClickUp.

        This method updates backlog task status, priority, and assignees in ClickUp
        based on the verified domain result.

        Args:
            result: Verified backlog task containing update information.
            name_to_email: Mapping of usernames to emails for resolution.
            email_to_id: Mapping of emails to ClickUp member IDs.
            ignore_names (bool):
                If True, names without an email mapping are ignored.
                If False, an exception is raised for unresolved names.
            ignore_mails (bool):
                If True, unresolved assignees are ignored.
                If False, an exception is raised when resolution fails.

        Returns:
            None.

        Raises:
            ClickUpTaskUpdateException: If the API request fails.
        """
        logger.info(
            "Updating backlog task. task_id=%s task_name=%s.",
            result.task_id,
            result.task_name,
        )

        endpoint = f"/task/{result.task_id}"

        payload = ClickUpTaskWriter._build_task_payload(result, include_name=False)


        if result.estimation is not None:
            payload["time_estimate"] = result.estimation * 3_600_000

        assignee_ids = ClickUpTaskWriter._resolve_assignee_ids(result, name_to_email, email_to_id, ignore_names,ignore_mails)

        if assignee_ids:
            payload["assignees"] = {"add": assignee_ids}

        self._put_task(endpoint, payload, task_id=result.task_id, task_name=result.task_name)

    @staticmethod
    def _build_task_payload(result, include_name: bool = True) -> dict:
        """
        Build a ClickUp task payload from a verified task result.

        This method converts verified task data into a payload compatible with
        the ClickUp API. Depending on the operation type, task name and
        description can optionally be included.

        Args:
            result:
                Verified task result containing task metadata such as name,
                description, status, and priority.
            include_name:
                If True, task name and description are included in the payload.
                Typically enabled for task creation and disabled for updates.

        Returns:
            dict: ClickUp API payload containing task fields to create or update.
        """
        payload = {}

        if include_name:
            payload["name"] = result.task_name
            payload["description"] = result.task_description

        if result.task_status:
            payload["status"] = result.task_status

        priority = priority_to_str(result.task_priority)
        if priority:
            payload["priority"] = priority

        return payload

    @staticmethod
    def _resolve_assignee_ids(result, name_to_email, email_to_id, ignore_names, ignore_mails) -> list:
        """
        Resolve ClickUp assignee IDs from verified task assignee names.

        This method extracts assignee names from the verified task result,
        resolves them into email addresses, and finally maps them to ClickUp
        member IDs.

        Args:
            result: Verified task result containing assignee information.
            name_to_email: Mapping of assignee names to email addresses.
            email_to_id: Mapping of email addresses to ClickUp member IDs.
            ignore_names:
                If True, unknown assignee names are ignored.
                If False, an exception is raised for unresolved names.
            ignore_mails:
                If True, unresolved email addresses are ignored.
                If False, an exception is raised when email resolution fails.

        Returns:
            list: List of resolved ClickUp member IDs.
        """
        assignee_names = []
        if result.task_assigne:
            assignee_names = [a.strip() for a in result.task_assigne.split(",")]

        assignee_ids = resolve_assignee_ids_strict(name_to_email, email_to_id, assignee_names, ignore_names,ignore_mails)

        return assignee_ids

    @staticmethod
    def _build_location_list_map(folders: List[FolderWithListsMetadata]) -> dict:
        """
        Build a mapping of location label to list ID.

        Location label format:
        - "FolderName / ListName" for lists inside a folder
        - "ListName" for folderless lists (folder.id == lst.id)

        Args:
            folders: Folder objects with lists metadata.

        Returns:
            Mapping of location label to list ID.
        """
        mapping = {}
        for folder in folders:
            for lst in folder.lists:
                label = lst.name if folder.id == lst.id else f"{folder.name} / {lst.name}"
                mapping[label] = lst.id
        return mapping

    def _post_task(self, endpoint: str, payload: dict, task_name: str, location: str, task_status: str) -> None:
        """
        Send a task creation request to the ClickUp API.

        This helper method performs the HTTP POST request used to create a task
        in ClickUp and centralizes logging and error handling for task creation
        operations.

        Args:
            endpoint: ClickUp API endpoint used for task creation.
            payload: Request payload containing task data.
            task_name: Name of the task being created.
            location: Target ClickUp folder/list location.
            task_status: Initial status assigned to the task.

        Returns:
            None.

        Raises:
            ClickUpTaskCreateException: Raised when the ClickUp API request fails.
        """
        response = self._http.post_raw(endpoint, payload)
        if response.status_code == 200:
            logger.info("Task created successfully. task_name=%s location=%s task_status=%s status_code=%d.",
                        task_name, location, task_status, response.status_code)
        else:
            logger.error("Task creation failed. task_name=%s location=%s status_code=%d response=%s.",
                         task_name, location, response.status_code, response.text)
            raise ClickUpTaskCreateException(
                f"The task \"{task_name}\" could not be created in ClickUp. Please try again or contact support."
            )

    def _put_task(self, endpoint: str, payload: dict, task_id: str, task_name: str) -> None:
        """
        Send a task update request to the ClickUp API.

        This helper method performs the HTTP PUT request used to update an
        existing ClickUp task and centralizes logging and error handling for
        task update operations.

        Args:
            endpoint: ClickUp API endpoint used for task updates.
            payload: Request payload containing updated task fields.
            task_id: Identifier of the ClickUp task being updated.
            task_name: Name of the task being updated.

        Returns:
            None.

        Raises:
            ClickUpTaskUpdateException: Raised when the ClickUp API request fails.
        """
        response = self._http.put_raw(endpoint, payload)
        if response.status_code == 200:
            logger.info("Task updated successfully. task_id=%s task_name=%s status_code=%d.",
                        task_id, task_name, response.status_code)
        else:
            logger.error("Task update failed. task_id=%s task_name=%s status_code=%d response=%s.",
                         task_id, task_name, response.status_code, response.text)
            raise ClickUpTaskUpdateException(
                f"The task \"{task_name}\" could not be updated in ClickUp. Please try again or contact support."
            )