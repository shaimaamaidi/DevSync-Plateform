"""
Task generation from backlog use case module.

This module provides the GenerateTaskFromBacklogUseCase class, which is responsible
for generating structured ClickUp tasks from a sprint backlog.
It coordinates retrieval of ClickUp space metadata and delegates task generation
to a dedicated generator service.

Classes:
    GenerateTaskFromBacklogUseCase: Main use case for generating tasks from a sprint backlog.
"""
import asyncio
import logging
from typing import List

from backend.src.domain.entities.generated_tasks.generated_task_from_backlog import GeneratedTaskFromBacklog
from backend.src.domain.entities.sprint.sprint import Sprint
from backend.src.domain.helpers.clickup_folder_helpers import get_folders_priorities
from backend.src.domain.ports.input.i_generate_tasks_from_backlog_use_case import IGenerateTasksFromBacklogUseCase
from backend.src.domain.ports.output.clickup.i_clickup_reader import IClickUpReader
from backend.src.domain.ports.services.task_generation_from_backlog.i_task_generator_from_backlog import ITaskGeneratorFromBacklog


logger = logging.getLogger(__name__)


class GenerateTasksFromBacklogUseCase(IGenerateTasksFromBacklogUseCase):
    """
    Application use case for generating ClickUp tasks from a sprint backlog.

    Coordinates retrieval of ClickUp space structure and transforms it into
    usable metadata (statuses, priorities), then delegates task generation
    to a task generator service.

    Attributes:
        _clickup_reader (IClickUpReader): Port used to fetch data from ClickUp API.
        _task_generator (ITaskGeneratorFromBacklog): Service responsible for generating tasks.
    """

    def __init__(self, clickup_reader: IClickUpReader, task_generator: ITaskGeneratorFromBacklog):
        """
        Initialize the use case with required services.

        Args:
            clickup_reader (IClickUpReader): ClickUp reader port implementation.
            task_generator (ITaskGenerator): Task generator service.
        """
        self._clickup_reader = clickup_reader
        self._task_generator = task_generator

    async def generate_tasks_from_backlog(self, sprint_backlog: List[Sprint], space_id: str) -> List[GeneratedTaskFromBacklog]:
        """
        Generate ClickUp tasks from a sprint backlog.

        This method retrieves the ClickUp space structure, extracts relevant
        metadata (statuses and priorities), and uses a task generator to
        produce structured tasks.

        Args:
            sprint_backlog (List[Sprint]): sprint backlog content.
            space_id (str): ClickUp space identifier.

        Returns:
            List[GeneratedTaskFromBacklog]: List of generated tasks.
        """
        logger.info(
            "Generating tasks from backlog: space_id=%s.",
            space_id,
        )

        folders = self._clickup_reader.get_space_structure_metadata(space_id)
        locations_priorities = get_folders_priorities(folders)

        results = await asyncio.gather(*[
            self._task_generator.generate_tasks(
                backlog=sprint,
                locations_priorities=locations_priorities,
            )
            for sprint in sprint_backlog
        ])

        tasks = [task for result in results if result for task in result]


        logger.info(
            "Tasks generated successfully: space_id=%s count=%d.",
            space_id,
            len(tasks),
        )

        return tasks