"""
ClickUp task saving use case module.

This module provides the SaveTaskInClickUpUseCase class, which is responsible
for applying verified tasks into ClickUp.
It coordinates retrieval of space structure, member resolution, and delegates
task persistence to a ClickUp writer.

Classes:
    SaveTaskInClickUpUseCase: Main use case for saving verified tasks into ClickUp.
"""

import logging
from typing import List

from backend.src.domain.entities.clickup.verified_task import VerifiedTask
from backend.src.domain.ports.input.i_clickup_task_service import IClickUpTaskService
from backend.src.domain.ports.input.i_save_task_in_clickup_use_case import ISaveTaskInClickUpUseCase
from backend.src.domain.ports.output.clickup.i_clickup_writer import IClickUpTaskWriter
from backend.src.domain.ports.repositories.i_member_repository import IMemberRepository


logger = logging.getLogger(__name__)


class SaveTaskInClickUpUseCase(ISaveTaskInClickUpUseCase):
    """
    Application use case for saving verified tasks into ClickUp.

    Coordinates retrieval of ClickUp space structure, resolves task assignees
    using member repository, and delegates task creation/update to a ClickUp writer.

    Attributes:
        _clickup_task_service (IClickUpTaskService): Service for ClickUp structure and members.
        _member_repo (IMemberRepository): Repository for resolving member identities.
        _clickup_writer (IClickUpTaskWriter): Writer responsible for applying tasks in ClickUp.
    """

    def __init__(
            self,
            clickup_task_service: IClickUpTaskService,
            member_repo: IMemberRepository,
            clickup_writer: IClickUpTaskWriter
    ):
        """
        Initialize the use case with required services and repositories.

        Args:
            clickup_task_service (IClickUpTaskService): ClickUp task service.
            member_repo (IMemberRepository): Member repository.
            clickup_writer (IClickUpTaskWriter): ClickUp writer.
        """
        self._clickup_task_service = clickup_task_service
        self._member_repo = member_repo
        self._clickup_writer = clickup_writer

    def save_to_clickup(
            self,
            tasks: List[VerifiedTask],
            space_id: str,
            ignore_names: bool,
            ignore_mails: bool
    ) -> None:
        """
        Apply verified tasks into ClickUp.

        This method retrieves the ClickUp space structure, resolves assignees
        based on extracted names, optionally fetches workspace members, and
        delegates task creation/update to the ClickUp writer.

        Args:
            tasks (List[VerifiedTask]): List of verified tasks to apply.
            space_id (str): ClickUp space identifier.
            ignore_names (bool): Whether to ignore name-based resolution.
            ignore_mails (bool): Whether to ignore email-based assignment.
        """
        logger.info(
            "Saving tasks to ClickUp: space_id=%s total_tasks=%d.",
            space_id,
            len(tasks),
        )

        folders = self._clickup_task_service.get_space_structure(space_id)

        self._clickup_task_service.invalidate(space_id)

        assignee_names_list: List[str] = list({
            a.strip()
            for task in tasks
            if task.task_assigne
            for a in task.task_assigne.split(",")
            if a.strip() and a.strip() != "غير محدد"
        })

        name_to_email: dict[str, str] = {}

        if assignee_names_list:
            name_to_email = self._member_repo.find_by_arabic_name(assignee_names_list,ignore_names)

        members: List[dict] = []

        if name_to_email :
            members = self._clickup_task_service.get_workspace_members(space_id)

        self._clickup_writer.apply_results(tasks, folders, members, name_to_email, ignore_mails)

        logger.info(
            "Tasks saved to ClickUp successfully: space_id=%s created_tasks=%d.",
            space_id,
            len(tasks),
        )