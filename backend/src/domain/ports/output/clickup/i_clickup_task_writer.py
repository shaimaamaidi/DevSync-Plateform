"""
Service port for applying task changes to ClickUp.

This module defines the IClickUpTaskWriter interface, which specifies operations
for creating or updating tasks in ClickUp based on verification results.
"""

from abc import abstractmethod, ABC
from typing import List

from backend.src.domain.entities.clickup.folder_with_list_metadata import FolderWithListsMetadata
from backend.src.domain.entities.clickup.list_with_tasks import ClickUpTask
from backend.src.domain.entities.verify_tasks.verified_task import VerifiedTask


class IClickUpTaskWriter(ABC):
    """
    Define ClickUp task writing behavior required by the application.

    This interface represents the contract for applying domain decisions
    (create/update tasks) to ClickUp using verified task results and
    workspace context.
    """

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def delete_task(self, task_id: str) -> bool:
        """
        Delete a task from ClickUp.

        This method sends a deletion request to the ClickUp API for the
        specified task identifier.

        Args:
            task_id: Identifier of the ClickUp task to delete.

        Returns:
            bool: True if task was deleted successfully.

        Raises:
            ClickUpTaskDeleteException:
                Raised when the ClickUp API deletion request fails.
        """
        pass

    @abstractmethod
    def apply_results(
            self,
            results: List[VerifiedTask],
            folders: List[FolderWithListsMetadata],
            members: List[dict],
            name_to_email: dict[str, str],
            ignore_names: bool,
            ignore_mails: bool
    ) -> None:
        """
        Apply verified task results to ClickUp.

        This method takes domain-level verification results and translates them
        into ClickUp operations (task creation or updates) using workspace context.

        Args:
            results: List of verification results describing actions to apply.
            folders: ClickUp space structure used to resolve folders and lists.
            members: Workspace members with their metadata (id, username, email).
            name_to_email: Mapping of usernames to email addresses.
            ignore_names (bool):Flag indicating whether name-based assignment should
                be ignored.
            ignore_mails (bool):Flag indicating whether email-based assignment should
                be ignored.

        Returns:
            None
        """
        pass