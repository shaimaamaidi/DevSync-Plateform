"""
Service port for saving verified ClickUp tasks.

This module defines the ISaveTaskInClickUpUseCase interface, which specifies
the operation for applying verified task results into ClickUp.

It acts as a contract for application-level services responsible for:
- Applying task creation and update operations
- Resolving workspace members and assignees
- Synchronizing verified domain results with ClickUp
"""

from typing import List

from backend.src.domain.entities.verify_tasks.verified_task import VerifiedTask


class ISaveTaskInClickUpUseCase:
    """
    Define ClickUp task persistence behavior required by the application.

    This interface represents the contract for applying verified task results
    into ClickUp, abstracting external ClickUp API operations and member
    resolution logic.
    """

    def save_to_clickup(
            self,
            tasks: List[VerifiedTask],
            space_id,
            ignore_names: bool,
            ignore_mails: bool
    ) -> None:
        """
        Apply verified tasks into ClickUp.

        Args:
            tasks (List[VerifiedTask]): List of verified task actions.
            space_id (str): ClickUp space identifier.
            ignore_names (bool): Whether to ignore name-based resolution.
            ignore_mails (bool): Whether to ignore email-based assignment.

        Returns:
            None
        """
        pass