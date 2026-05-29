"""
Task search use case module.

This module provides the SearchTaskUseCase class, which is responsible for
orchestrating the search of ClickUp tasks based on a natural language question.

It coordinates retrieval of ClickUp workspace structure, delegates semantic
search logic to a task search service, and formats a user-facing response
depending on the number of results found.

Classes:
    SearchTaskUseCase: Main use case for searching tasks in ClickUp.
"""

import logging

from backend.src.domain.entities.checked_task_status.task_search_response import TaskSearchResponse, TaskSearchStatus
from backend.src.domain.ports.input.task_status_check.i_search_task_use_case import ISearchTaskUseCase
from backend.src.domain.ports.output.clickup.i_clickup_reader import IClickUpReader
from backend.src.domain.ports.services.task_status_checking.i_task_search import ITaskSearch


logger = logging.getLogger(__name__)


class SearchTaskUseCase(ISearchTaskUseCase):
    """
    Application use case for searching ClickUp tasks.

    This use case orchestrates the task search flow by:
    - Fetching ClickUp workspace structure for a given space
    - Checking if tasks exist in the workspace
    - Delegating semantic search to a task search service
    - Formatting a user-friendly response based on search results

    Attributes:
        _clickup_reader (IClickUpReader): Port used to fetch data from ClickUp API.
        _task_search (ITaskSearch): Service responsible for semantic task search logic.
    """

    def __init__(
        self,
        clickup_reader: IClickUpReader,
        task_search: ITaskSearch,
    ):
        """
        Initialize the SearchTaskUseCase.

        Args:
            clickup_reader: ClickUp reader port implementation used to retrieve workspace data.
            task_search: Service responsible for searching tasks using semantic or LLM-based logic.
        """
        self._clickup_reader = clickup_reader
        self._task_search = task_search

    def search_task(self, description: str, space_id: str) -> TaskSearchResponse:
        """
        Search ClickUp tasks based on a natural language question.

        This method:
        - Retrieves the full structure of the ClickUp space
        - Validates whether tasks exist in the space
        - Executes semantic task search
        - Returns a structured response depending on result count:
            - 0 tasks: informs user no matches were found
            - 1 task: asks user confirmation for the matched task
            - multiple tasks: asks user to choose from top results

        Args:
            description: Natural language phrase describing the search intent.
            space_id: Identifier of the ClickUp space to search within.

        Returns:
            TaskSearchResponse: User-facing response containing:
                - A message guiding the user
                - A list of matched ClickUp tasks (if any)
        """
        logger.info(
            "Search task in ClickUp: space_id=%s description=%s.",
            space_id,
            description,
        )

        folders = self._clickup_reader.get_space_full_structure(space_id)

        has_tasks = any(task for folder in folders for lst in folder.lists for task in lst.tasks)

        if not has_tasks:
            logger.warning("No tasks found in space. space_id=%s.", space_id)
            return TaskSearchResponse(
                status=TaskSearchStatus.NO_TASKS_IN_SPACE,
                message="The selected space does not contain any tasks to search.",
                task=[]
            )

        results =  self._task_search.search_task(description, folders)

        logger.info(
            "Task search completed successfully: space_id=%s tasks_result=%d.",
            space_id,
            len(results),
        )

        if len(results) == 0:
            return TaskSearchResponse(
                status=TaskSearchStatus.NO_MATCH,
                message="No tasks found matching your query. Please try rephrasing your question.",
                task=[]
            )
        elif len(results) == 1:
            return TaskSearchResponse(
                status=TaskSearchStatus.SINGLE_MATCH,
                message=f"I found one task matching your query: **{results[0].name}**. Is this the task you are referring to?",
                task=results
            )
        else:
            return TaskSearchResponse(
                status=TaskSearchStatus.MULTIPLE_MATCHES,
                message="I found multiple tasks matching your query. Please select the one you are referring to.",
                task=results[:3]
            )
