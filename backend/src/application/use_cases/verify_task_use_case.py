"""
ClickUp task verification use case module.

This module provides the VerifyTaskUseCase class, which is responsible for verifying
tasks against existing ClickUp tasks.
It organizes tasks by folder and delegates comparison logic to a verifier service.

Classes:
    VerifyTaskUseCase: Main use case for verifying generated tasks.
"""

import logging
from typing import List

from backend.src.domain.entities.generate_tasks_from_summary.generated_task import GeneratedTask
from backend.src.domain.entities.verify_tasks.verified_task import VerifiedTask
from backend.src.domain.helpers.clickup_folder_helpers import get_generated_tasks_by_location, get_tasks_by_location

from backend.src.domain.ports.input.i_verify_task_use_case import IVerifyTaskUseCase
from backend.src.domain.ports.output.clickup.i_clickup_reader import IClickUpReader
from backend.src.domain.ports.repositories.i_member_repository import IMemberRepository
from backend.src.domain.ports.services.clickup_task_verification.i_clickup_task_verifier import \
    IClickUpTaskVerifier


logger = logging.getLogger(__name__)


class VerifyTaskUseCase(IVerifyTaskUseCase):
    """
    Application use case for verifying generated ClickUp tasks.

    Compares tasks with existing tasks from ClickUp by organizing them
    per folder, then delegates verification logic to a task verifier service.

    Attributes:
        _clickup_reader (IClickUpReader): Port used to fetch data from ClickUp API.
        _task_verifier (IClickUpTaskVerifier): Service responsible for task verification logic.
        _member_repo (IMemberRepository): Repository for resolving member identities.
    """

    def __init__(
        self,
        clickup_reader: IClickUpReader,
        task_verifier: IClickUpTaskVerifier,
        member_repo: IMemberRepository
    ):
        """
        Initialize the use case with required services.

        Args:
            clickup_reader (IClickUpReader): ClickUp reader port implementation.
            task_verifier (IClickUpTaskVerifier): Task verifier service.
            member_repo (IMemberRepository): Member repository.
        """
        self._clickup_reader = clickup_reader
        self._task_verifier = task_verifier
        self._member_repo =member_repo


    def verify_tasks(self, tasks: List[GeneratedTask], space_id) -> List[VerifiedTask]:
        """
        Verify tasks against existing ClickUp tasks.

        This method retrieves the current ClickUp space structure, groups both
        existing and generated tasks by folder, and performs verification
        folder by folder using a dedicated verifier service.

        Args:
            tasks (List[GeneratedTask]): List of generated tasks.
            space_id (str): ClickUp space identifier.

        Returns:
            List[VerifiedTask]: List of verified tasks with corresponding actions.
        """
        logger.info(
            "Verifying tasks in ClickUp: space_id=%s tasks=%d.",
            space_id,
            len(tasks),
        )

        folders = self._clickup_reader.get_space_full_structure(space_id)

        existing_by_location = get_tasks_by_location(folders)

        assignee_mails_list: List[str] = list({
            email.strip()
            for existing_tasks in existing_by_location.values()
            for task in existing_tasks
            if task.assignee
            for email in task.assignee.split(",")
            if email.strip()
        })

        email_to_name: dict[str, str] = {}

        if assignee_mails_list:
            email_to_name = self._member_repo.find_by_mails(assignee_mails_list)

        for existing_tasks in existing_by_location.values():
            for task in existing_tasks:
                if not task.assignee:
                    continue

                resolved_names = [
                    email_to_name[email.strip()]
                    for email in task.assignee.split(",")
                    if email.strip() and email.strip() in email_to_name
                ]

                task.assignee = ", ".join(resolved_names) if resolved_names else "غير محدد"

        generated_by_location = get_generated_tasks_by_location(tasks)

        all_results = []
        for location, gen_tasks in generated_by_location.items():
            existing = existing_by_location.get(location, [])
            results = self._task_verifier.verify_tasks(
                existing_tasks=existing,
                tasks=gen_tasks,
            )

            all_results.extend(results)

        logger.info(
            "Task verification completed successfully: space_id=%s create_or_update_tasks=%d.",
            space_id,
            len(all_results),
        )

        return all_results
