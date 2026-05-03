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
from backend.src.domain.helpers.clickup_folder_helpers import get_tasks_by_folder,\
    get_generated_tasks_by_folder
from backend.src.domain.ports.input.i_clickup_task_service import IClickUpTaskService
from backend.src.domain.ports.input.i_verify_task_use_case import IVerifyTaskUseCase
from backend.src.domain.ports.services.clickup_task_verification.i_clickup_task_verifier import \
    IClickUpTaskVerifier


logger = logging.getLogger(__name__)


class VerifyTaskUseCase(IVerifyTaskUseCase):
    """
    Application use case for verifying generated ClickUp tasks.

    Compares tasks with existing tasks from ClickUp by organizing them
    per folder, then delegates verification logic to a task verifier service.

    Attributes:
        _clickup_task_service (IClickUpTaskService): Service for retrieving ClickUp structure.
        _task_verifier (IClickUpTaskVerifier): Service responsible for task verification logic.
    """

    def __init__(self, clickup_task_service: IClickUpTaskService, task_verifier: IClickUpTaskVerifier):
        """
        Initialize the use case with required services.

        Args:
            clickup_task_service (IClickUpTaskService): ClickUp task service.
            task_verifier (IClickUpTaskVerifier): Task verifier service.
        """
        self._clickup_task_service = clickup_task_service
        self._task_verifier = task_verifier


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

        folders = self._clickup_task_service.get_space_structure(space_id)

        existing_by_folder = get_tasks_by_folder(folders)
        generated_by_folder = get_generated_tasks_by_folder(tasks)

        all_results = []
        for folder_name, gen_tasks in generated_by_folder.items():
            existing = existing_by_folder.get(folder_name, [])
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
