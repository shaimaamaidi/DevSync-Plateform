"""
Commit-to-task mapping use case module.

This module provides the MapCommitTaskUseCase class, which is responsible
for orchestrating the mapping between a GitHub commit and its corresponding
ClickUp task.

It retrieves the full ClickUp space structure, flattens available tasks,
and delegates semantic matching to an LLM-based commit-task mapper.

Classes:
    MapCommitTaskUseCase: Main use case for mapping commits to ClickUp tasks.
"""

import logging

from backend.src.domain.entities.mapped_commit_task.mapped_commit_task_reponse import MappedCommitTaskResponse, \
    CommitTaskMappingStatus
from backend.src.domain.ports.input.i_map_commit_task_use_case import IMapCommitTaskUseCase
from backend.src.domain.ports.output.clickup.i_clickup_reader import IClickUpReader
from backend.src.domain.ports.services.commit_task_mapping.i_commit_task_mapper import ICommitTaskMapper


logger = logging.getLogger(__name__)


class MapCommitTaskUseCase(IMapCommitTaskUseCase):
    """
    Application use case for mapping a GitHub commit to a ClickUp task.

    Coordinates retrieval of ClickUp space structure, extracts all tasks,
    and delegates the semantic mapping logic to the ICommitTaskMapper
    service (LLM-based implementation).

    Attributes:
        _clickup_reader (IClickUpReader): Port used to read ClickUp data.
        _commit_task_mapper (ICommitTaskMapper): Service responsible for LLM-based mapping.
    """

    def __init__(
        self,
        clickup_reader: IClickUpReader,
        commit_task_mapper: ICommitTaskMapper
    ):
        """
        Initialize the MapCommitTaskUseCase.

        Args:
            clickup_reader (IClickUpReader): ClickUp data access port.
            commit_task_mapper (ICommitTaskMapper): Commit-to-task mapping service.
        """
        self._clickup_reader = clickup_reader
        self._commit_task_mapper = commit_task_mapper

    def map_commit_task(self, commit: str, space_id: str) -> MappedCommitTaskResponse:
        """
        Map a GitHub commit to a ClickUp task within a given space.

        This method:
        - Retrieves full ClickUp space structure
        - Flattens all tasks from folders and lists
        - Delegates mapping to LLM-based mapper service
        - Returns the matched task if found

        Args:
            commit: GitHub commit message or identifier.
            space_id: ClickUp space identifier.

        Returns:
            MappedCommitTaskResponse:
        """
        logger.info("Mapping commit to task. space_id=%s.", space_id)

        folder_with_tasks = self._clickup_reader.get_space_full_structure(space_id)

        tasks =[
            task
            for folder in folder_with_tasks
            for lst in folder.lists
            for task in lst.tasks
        ]

        if not tasks:
            return MappedCommitTaskResponse(
                status=CommitTaskMappingStatus.CLICK_UP_EMPTY,
                message="The selected space does not contain any tasks to compare with this commit.",
                task=None
            )

        result = self._commit_task_mapper.map_commit_task(commit, tasks)

        if not result:
            logger.warning("No matching task found for commit: %s.", commit)
            return MappedCommitTaskResponse(
                status=CommitTaskMappingStatus.NOT_FOUND,
                message="I couldn't find a ClickUp task matching this commit.",
                task=None
            )

        logger.info(
            "Mapping commit to task computation completed successfully: space_id=%s task_id=%s.",
            space_id,
            result.task_id,
        )

        return MappedCommitTaskResponse(
            status=CommitTaskMappingStatus.FOUND,
            message = f"This commit has been successfully linked to the ClickUp task: **{result.name}**.",
            task=result
        )
