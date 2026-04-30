"""
Service port for applying task changes to ClickUp.

This module defines the IClickUpTaskWriter interface, which specifies operations
for creating or updating tasks in ClickUp based on verification results.
"""

from typing import List

from backend.src.domain.entities.clickup.folder import Folder
from backend.src.domain.entities.clickup.verified_task import VerifiedTask


class IClickUpTaskWriter:
    """
    Define ClickUp task writing behavior required by the application.

    This interface represents the contract for applying domain decisions
    (create/update tasks) to ClickUp using verified task results and
    workspace context.
    """

    def apply_results(
        self,
        results: List[VerifiedTask],
        folders: List[Folder],
        members: List[dict],
        name_to_email: dict[str, str]
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

        Returns:
            None
        """
        pass