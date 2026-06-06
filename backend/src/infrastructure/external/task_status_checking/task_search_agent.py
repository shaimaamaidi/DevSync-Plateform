"""
ClickUp task search agent.

This module defines the TaskSearchAgent, responsible for searching
ClickUp tasks based on a natural language query using an LLM.

It transforms a user description and a list of candidate tasks into
the most relevant matching tasks by applying semantic similarity
through an LLM.
"""

import asyncio
import logging
import json
from typing import List

from backend.src.domain.entities.checked_task_status.task_search_result import TaskSearchResult
from backend.src.domain.entities.clickup.folder_with_lists import FolderWithLists
from backend.src.domain.entities.clickup.list_with_tasks import ClickUpTask
from backend.src.domain.ports.services.prompt_loading.i_prompt_loader import IPromptLoader
from backend.src.domain.ports.services.task_status_checking.i_task_search import ITaskSearch
from backend.src.infrastructure.external.shared.agents.base_agent import BaseAgent
from backend.src.infrastructure.prompts.prompt_loader import PromptLoader

logger = logging.getLogger(__name__)


class TaskSearchAgent(BaseAgent[TaskSearchResult], ITaskSearch):
    """
    LLM-based implementation of ITaskSearch.

    This agent is responsible for:
    - Interpreting a natural language search query
    - Matching it against a list of ClickUp tasks
    - Using an LLM to compute semantic relevance scores
    - Returning the most relevant tasks above a confidence threshold
    """
    _POOL_SIZE = 20

    def __init__(self, prompt_loader: IPromptLoader):
        """
        Initialize the TaskSearchAgent.

        Args:
            prompt_loader (IPromptLoader): Service responsible for loading
                prompt templates used by the agent during LLM interactions.
        """
        super().__init__(prompt_loader)

    async def search_task(
        self,
        description: str,
        tasks: List[ClickUpTask]
    ) -> List[ClickUpTask]:
        """
        Search and rank ClickUp tasks based on a natural language query.

        This method performs semantic task search using an LLM by:
        - Splitting tasks into smaller batches (pooling)
        - Running parallel LLM evaluations on each batch
        - Collecting candidate matches with confidence scores
        - Filtering low-confidence results
        - Selecting the top-ranked tasks (top-3)

        The final result is a small set of tasks that best match
        the user description.

        Args:
            description: Natural language query describing the user's intent.
            tasks: List of ClickUp tasks to evaluate.

        Returns:
            List[ClickUpTask]: The top matching tasks ranked by confidence.

        Raises:
            LLMNetworkException: If a network error occurs while contacting the LLM.
            LLMApiException: If the LLM API returns an error response.
            LLMParsingException: If the LLM response cannot be parsed correctly.
        """
        logger.info("Searching task process from a user description.")

        pools = [tasks[i:i + self._POOL_SIZE] for i in range(0, len(tasks), TaskSearchAgent._POOL_SIZE)]

        results = await asyncio.gather(*[
            self._find_tasks_by_description(description, pool)
            for pool in pools
        ])

        all_candidates = [
            candidate
            for pool_result in results
            if pool_result and pool_result.candidates
            for candidate in pool_result.candidates
            if candidate.confidence >= 0.65
        ]

        all_candidates.sort(key=lambda x: x.confidence, reverse=True)
        top_candidates = all_candidates[:3]

        if not top_candidates:
            return []

        task_map = {task.id: task for task in tasks}

        logger.info(
            "Task searching from user question completed successfully: %d task(s) found.",
            len(top_candidates)
        )

        return [task_map[c.id] for c in top_candidates if c.id in task_map]

    async def _find_tasks_by_description(self, description: str, pool: List[ClickUpTask]) -> TaskSearchResult:
        """
        Evaluate a batch of tasks against a natural language query using an LLM.

        This method:
        - Serializes a subset (pool) of tasks into JSON
        - Sends the user description and task batch to the LLM
        - Uses a structured prompt to compute task relevance
        - Returns a structured TaskSearchResult containing candidates

        Args:
            description: Natural language query describing the search intent.
            pool: Subset of ClickUp tasks to evaluate.

        Returns:
            TaskSearchResult: LLM-generated result containing candidate tasks
            with associated confidence scores.
        """
        tasks_json = json.dumps(
            [task.to_dict() for task in pool],
            ensure_ascii=False,
            indent=2
        )
        return await asyncio.to_thread(
            self._call_llm,
            agent_name="TaskSearchAgent",
            folder_name="task_status_checking",
            prompt_name="task_search_agent",
            variables={"user_description": description, "tasks_json": tasks_json},
            response_format=TaskSearchResult,
        )