"""
ClickUp task search agent.

This module defines the TaskSearchAgent, responsible for searching
ClickUp tasks based on a natural language question using an LLM.
It transforms a user query and existing workspace structure into
relevant task matches.
"""

import logging
import json
from typing import List

from backend.src.domain.entities.checked_task_status.task_search_result import TaskSearchResult
from backend.src.domain.entities.clickup.folder_with_lists import FolderWithLists
from backend.src.domain.entities.clickup.list_with_tasks import ClickUpTask
from backend.src.domain.ports.services.prompt_loading.i_prompt_loader import IPromptLoader
from backend.src.domain.ports.services.task_status_checking.i_task_search import ITaskSearch
from backend.src.infrastructure.external.shared.agents.base_agent import BaseAgent


logger = logging.getLogger(__name__)


class TaskSearchAgent(BaseAgent[TaskSearchResult], ITaskSearch):
    """
    LLM-based implementation of ITaskSearch.

    This agent is responsible for:
    - Interpreting a natural language question
    - Searching relevant ClickUp tasks across folders and lists
    - Using an LLM to match user intent with existing task data
    """

    def __init__(self, prompt_loader: IPromptLoader):
        """
        Initialize the TaskSearchAgent.

        Args:
            prompt_loader (IPromptLoader): Service responsible for loading
                prompt templates used by the agent during LLM interactions.
        """
        super().__init__(prompt_loader)

    def search_task(
        self,
        description: str,
        folder_with_tasks: List[FolderWithLists]
    ) -> List[ClickUpTask]:
        """
        Search ClickUp tasks based on a user question using an LLM.

        This method:
        - Flattens all tasks from folders and lists into a JSON structure
        - Sends the user query and task dataset to the LLM
        - Parses the LLM response into structured task search results

        Args:
            description: User natural language phrase describing the search intent.
            folder_with_tasks: List of folders containing ClickUp lists and tasks.

        Returns:
            List[ClickUpTask]: Tasks that match the user query.

        Raises:
            LLMNetworkException: If a network error occurs while contacting the LLM.
            LLMApiException: If the LLM API returns an error response.
            LLMParsingException: If the LLM response cannot be parsed correctly.
        """
        logger.info("Searching task process from a user description.")

        tasks_json = json.dumps(
            [task.to_dict() for folder in folder_with_tasks for lst in folder.lists for task in lst.tasks],
            ensure_ascii=False,
            indent=2
        )

        parsed: TaskSearchResult = self._call_llm(
            agent_name="TaskSearchAgent",
            folder_name="task_status_checking",
            prompt_name="task_search_agent",
            variables={
                "user_description": description,
                "tasks_json": tasks_json
            },
            response_format=TaskSearchResult,
        )

        if not parsed or not parsed.ids:
            logger.warning("No tasks extracted from the user question.")
            return []

        all_tasks = {
            task.id: task
            for folder in folder_with_tasks
            for lst in folder.lists
            for task in lst.tasks
        }

        matched_tasks = [all_tasks[task_id] for task_id in parsed.ids if task_id in all_tasks]

        logger.info(
            "Task searching from user question completed successfully: %d task(s) found.",
            len(matched_tasks)
        )

        return matched_tasks