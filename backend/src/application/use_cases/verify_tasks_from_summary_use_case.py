"""
ClickUp task verification use case module.

This module provides the VerifyTaskUseCase class, which is responsible for verifying
tasks generated from a summary against existing ClickUp tasks.
It organizes tasks by folder and delegates comparison logic to a verifier service.

Classes:
    VerifyTasksFromSummaryUseCase: Main use case for verifying generated tasks.
"""

import logging
from typing import List

from backend.src.domain.entities.generated_tasks.generated_task_from_summary import GeneratedTaskFromSummary
from backend.src.domain.entities.verified_tasks.verified_task_from_summary import VerifiedTaskFromSummary
from backend.src.domain.helpers.clickup_folder_helpers import get_generated_tasks_from_summary_by_location, get_tasks_by_location

from backend.src.domain.ports.input.i_verify_tasks_from_summary_use_case import IVerifyTasksFromSummaryUseCase
from backend.src.domain.ports.output.clickup.i_clickup_reader import IClickUpReader
from backend.src.domain.ports.repositories.i_member_repository import IMemberRepository
from backend.src.domain.ports.services.task_verification.i_task_from_summary_verifier import \
    ITaskFromSummaryVerifier


logger = logging.getLogger(__name__)


class VerifyTasksFromSummaryUseCase(IVerifyTasksFromSummaryUseCase):
    """
    Application use case for verifying generated ClickUp tasks.

    Compares tasks with existing tasks from ClickUp by organizing them
    per folder, then delegates verification logic to a task verifier service.

    Attributes:
        _clickup_reader (IClickUpReader): Port used to fetch data from ClickUp API.
        _task_verifier (ITaskFromSummaryVerifier): Service responsible for task verification logic.
        _member_repo (IMemberRepository): Repository for resolving member identities.
    """

    def __init__(
        self,
        clickup_reader: IClickUpReader,
        task_verifier: ITaskFromSummaryVerifier,
        member_repo: IMemberRepository
    ):
        """
        Initialize the use case with required services.

        Args:
            clickup_reader (IClickUpReader): ClickUp reader port implementation.
            task_verifier (ITaskFromSummaryVerifier): Task verifier service.
            member_repo (IMemberRepository): Member repository.
        """
        self._clickup_reader = clickup_reader
        self._task_verifier = task_verifier
        self._member_repo =member_repo

    def verify_tasks(self, tasks: List[GeneratedTaskFromSummary], space_id) -> List[VerifiedTaskFromSummary]:
        """
        Verify tasks against existing ClickUp tasks.

        This method retrieves the current ClickUp space structure, groups both
        existing and generated tasks by folder, and performs verification
        folder by folder using a dedicated verifier service.

        Args:
            tasks (List[GeneratedTaskFromSummary]): List of generated tasks.
            space_id (str): ClickUp space identifier.

        Returns:
            List[VerifiedTaskFromSummary]: List of verified tasks with corresponding actions.
        """
        logger.info(
            "Verifying tasks in ClickUp: space_id=%s tasks=%d.",
            space_id,
            len(tasks),
        )

        folders = self._clickup_reader.get_space_full_structure(space_id)

        has_tasks = any(task for folder in folders for lst in folder.lists for task in lst.tasks)

        if not has_tasks:
            logger.warning("No tasks found in space. space_id=%s.", space_id)
            return VerifyTasksFromSummaryUseCase._map_generated_to_verified_task(tasks)

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

        generated_by_location = get_generated_tasks_from_summary_by_location(tasks)

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

    @staticmethod
    def _map_generated_to_verified_task(generated_tasks: List[GeneratedTaskFromSummary]) -> List[VerifiedTaskFromSummary]:
        return [
            VerifiedTaskFromSummary(
                action="create",
                task_name=task.task_name,
                task_description=task.task_description,
                task_assigne=task.task_assigne,
                task_status=task.task_status,
                task_priority=task.task_priority,
                location=task.location,
                task_id=None,
            )
            for task in generated_tasks
        ]