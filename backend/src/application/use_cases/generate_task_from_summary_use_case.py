"""
Task generation from summary use case module.

This module provides the GenerateTaskFromSummaryUseCase class, which is responsible
for generating structured ClickUp tasks from a meeting summary.
It coordinates retrieval of ClickUp space metadata and delegates task generation
to a dedicated generator service.

Classes:
    GenerateTaskFromSummaryUseCase: Main use case for generating tasks from a meeting summary.
"""

import logging
from typing import List

from backend.src.domain.entities.generate_tasks_from_summary.generated_task import GeneratedTask
from backend.src.domain.helpers.clickup_folder_helpers import get_folders_statuses_and_priorities
from backend.src.domain.ports.input.i_clickup_task_service import IClickUpTaskService
from backend.src.domain.ports.input.i_generate_task_from_summary_use_case import IGenerateTaskFromSummaryUseCase
from backend.src.domain.ports.services.task_generation_from_summary.i_task_generator import ITaskGenerator


logger = logging.getLogger(__name__)


class GenerateTaskFromSummaryUseCase(IGenerateTaskFromSummaryUseCase):
    """
    Application use case for generating ClickUp tasks from a meeting summary.

    Coordinates retrieval of ClickUp space structure and transforms it into
    usable metadata (statuses, priorities), then delegates task generation
    to a task generator service.

    Attributes:
        _clickup_task_service (IClickUpTaskService): Service to retrieve ClickUp structure.
        _task_generator (ITaskGenerator): Service responsible for generating tasks.
    """

    def __init__(self, clickup_task_service: IClickUpTaskService, task_generator: ITaskGenerator):
        """
        Initialize the use case with required services.

        Args:
            clickup_task_service (IClickUpTaskService): ClickUp task service.
            task_generator (ITaskGenerator): Task generator service.
        """
        self._clickup_task_service = clickup_task_service
        self._task_generator = task_generator

    def generate_tasks_from_meeting_summary(self, meeting_summary: str, space_id) -> List[GeneratedTask]:
        """
        Generate ClickUp tasks from a meeting summary.

        This method retrieves the ClickUp space structure, extracts relevant
        metadata (statuses and priorities), and uses a task generator to
        produce structured tasks.

        Args:
            meeting_summary (str): Unstructured meeting summary text.
            space_id (str): ClickUp space identifier.

        Returns:
            List[GeneratedTask]: List of generated tasks.
        """
        logger.info(
            "Generating tasks from meeting summary: space_id=%s.",
            space_id,
        )

        folders = self._clickup_task_service.get_space_structure(space_id)
        locations_statuses = get_folders_statuses_and_priorities(folders)

        tasks = self._task_generator.generate_tasks(
            meeting_summary=meeting_summary,
            locations_statuses=locations_statuses,
        )
        tasks = tasks or []


        logger.info(
            "Tasks generated successfully: space_id=%s count=%d.",
            space_id,
            len(tasks),
        )

        return tasks