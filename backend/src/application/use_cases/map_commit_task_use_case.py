"""
Commit-to-task mapping use case module.

This module provides the MapCommitTaskUseCase class, responsible for
orchestrating the mapping between a GitHub commit and its most relevant
ClickUp task.

The use case:
- Retrieves the full ClickUp space structure
- Extracts and enriches tasks with contextual metadata
- Filters eligible tasks based on recency rules
- Delegates semantic matching to an LLM-based mapper

This component acts as the application layer orchestrator between
ClickUp data sources and the AI-based mapping engine.

Classes:
    MapCommitTaskUseCase: Main use case for mapping commits to ClickUp tasks.
"""

import logging

from backend.src.application.use_cases.shared.task_search_candidates import filter_search_candidates
from backend.src.domain.entities.mapped_commit_task.mapped_commit_task_reponse import MappedCommitTaskResponse, \
    CommitTaskMappingStatus
from backend.src.domain.ports.input.i_map_commit_task_use_case import IMapCommitTaskUseCase
from backend.src.domain.ports.output.clickup.i_clickup_reader import IClickUpReader
from backend.src.domain.ports.services.commit_task_mapping.i_commit_task_mapper import ICommitTaskMapper


logger = logging.getLogger(__name__)


class MapCommitTaskUseCase(IMapCommitTaskUseCase):
    """
    Application use case for mapping a GitHub commit to a ClickUp task.

    This class orchestrates the full workflow:
    - Fetch ClickUp space structure via IClickUpReader
    - Flatten tasks from folders and lists
    - Enrich tasks with contextual metadata (dates, updates, etc.)
    - Filter tasks based on eligibility rules (recency)
    - Delegate semantic matching to ICommitTaskMapper (LLM-based service)
    - Build a structured response for the API layer

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

    async def map_commit_task(self, commit: str, space_id: str) -> MappedCommitTaskResponse:
        """
        Map a GitHub commit to the most relevant ClickUp task within a space.

        Workflow:
        1. Retrieve full ClickUp space structure
        2. Flatten tasks from folders and lists
        3. Enrich tasks with contextual metadata using fetch_task_context
        4. Filter tasks created within the last 30 days
        5. Sort eligible tasks by most recently updated
        6. Delegate matching to the LLM-based commit-task mapper
        7. Return structured mapping response

        Filtering rules:
        - Only tasks created within the last 30 days are considered
        - If no eligible tasks exist, mapping is aborted early
        - If no LLM match is found, status = NOT_FOUND
        - Otherwise, return FOUND with matched task

        Args:
            commit (str):
                GitHub commit message or identifier.

            space_id (str):
                Identifier of the ClickUp space to search within.

        Returns:
            MappedCommitTaskResponse:
                Structured response containing:
                - mapping status (FOUND / NOT_FOUND / CLICK_UP_EMPTY)
                - message describing the result
                - matched task if found, otherwise None
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

        eligible_tasks = await filter_search_candidates(self._clickup_reader, tasks)

        if not eligible_tasks:
            return MappedCommitTaskResponse(
                status=CommitTaskMappingStatus.NOT_FOUND,
                message="No tasks found within the last 30 days to compare with this commit.",
                task=None
            )

        result = self._commit_task_mapper.map_commit_task(commit, eligible_tasks)

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
