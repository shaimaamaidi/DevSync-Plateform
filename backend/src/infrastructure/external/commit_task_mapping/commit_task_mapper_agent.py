"""
Commit-to-task mapping agent.

This module defines the CommitTaskMapperAgent, responsible for analyzing
GitHub commit messages and mapping them to the most relevant ClickUp tasks.

It uses LLM-based reasoning to:
- Interpret commit semantics and intent
- Compare commit messages against available ClickUp tasks
- Identify the most relevant ClickUp task for a given commit
- Ensure traceability between GitHub commits and ClickUp task execution

This component is part of the project tracking pipeline, enabling
cross-referencing between development activity and task management systems.
"""

import logging
import json
from typing import List

from backend.src.domain.entities.clickup.list_with_tasks import ClickUpTask
from backend.src.domain.entities.mapped_commit_task.mapped_commit_task_result import CommitTaskMapperResult
from backend.src.domain.ports.services.commit_task_mapping.i_commit_task_mapper import ICommitTaskMapper
from backend.src.domain.ports.services.prompt_loading.i_prompt_loader import IPromptLoader
from backend.src.infrastructure.external.shared.agents.base_agent import BaseAgent


logger = logging.getLogger(__name__)


class CommitTaskMapperAgent (BaseAgent[CommitTaskMapperResult], ICommitTaskMapper):
    """
    LLM-based implementation of ICommitTaskMapper.

    This agent maps GitHub commit messages to ClickUp tasks using LLM-based semantic matching.

    Responsibilities:
    - Analyze commit messages using LLM reasoning
    - Compare commits with a pool of ClickUp tasks
    - Select the most relevant task based on confidence scoring
    - Ensure traceability between source code changes and project management tasks
    """

    _POOL_SIZE = 15

    def __init__(self, prompt_loader: IPromptLoader):
        """
        Initialize the CommitTaskMapperAgent.

        Args:
            prompt_loader (IPromptLoader): Service responsible for loading
                prompt templates used by the agent during LLM interactions.
        """
        super().__init__(prompt_loader)

    def map_commit_task(
        self,
        commit: str,
        tasks: List[ClickUpTask],
    ) -> ClickUpTask | None:
        """
        Map a GitHub commit message to the most relevant ClickUp task.

        The process works as follows:
        - Tasks are split into smaller pools to improve LLM context handling
        - Each pool is evaluated independently using an LLM call
        - The agent selects the best candidate based on confidence thresholds
        - A final task is returned if a valid match is found

        Confidence rules:
        - Ignore results with confidence < 0.75
        - Immediately accept results with confidence ≥ 0.9
        - Otherwise, keep the highest confidence candidate across pools

        Args:
            commit (str): GitHub commit message or identifier describing a code change.
            tasks (List[ClickUpTask]): List of available ClickUp tasks to match against.

        Returns:
            ClickUpTask | None: The most relevant matched task if found, otherwise None.

        Raises:
            LLMNetworkException: If a network error occurs during LLM communication.
            LLMApiException: If the LLM API returns an error response.
            LLMParsingException: If the LLM response cannot be parsed into the expected format.
        """
        logger.info("Mapping commit to task process.")

        pools = CommitTaskMapperAgent.build_pools(tasks)

        best_candidate = None

        for pool in pools:
            result = self._find_task_by_commit(commit, pool)

            if not result or not result.id or not result.confidence:
                continue

            if result.confidence < 0.75:
                continue

            if result and result.confidence and result.confidence >= 0.9:
                best_candidate = result
                break

            if best_candidate is None or (result.confidence and result.confidence > best_candidate.confidence):
                best_candidate = result

        if not best_candidate:
            logger.warning("No task found for the commit: %s.", commit)
            return None

        all_tasks = {task.id: task for task in tasks}

        matched_task = all_tasks.get(best_candidate.id)

        if not matched_task:
            logger.warning("Task id returned by LLM not found in input tasks. id=%s.", best_candidate.id or "N/A")
            return None

        logger.info(
            "Commit to task mapping completed successfully: task_id=%s.",
            matched_task.id,
        )

        return matched_task

    def _find_task_by_commit(
        self,
        commit: str,
        tasks: List[ClickUpTask],
    ) -> CommitTaskMapperResult:
        """
        Use an LLM to identify the most relevant ClickUp task for a given commit
        within a limited pool of tasks.

        This method:
        - Serializes the task pool into JSON format
        - Sends commit + task context to the LLM
        - Parses the LLM response into a structured CommitTaskMapperResult

        Args:
            commit (str): The commit message to analyze.
            tasks (List[ClickUpTask]): A subset (pool) of ClickUp tasks to evaluate.

        Returns:
            CommitTaskMapperResult: Structured LLM result containing the best matched task ID
                and confidence score.
        """
        tasks_json = json.dumps(
            [task.to_dict() for task in tasks],
            ensure_ascii=False,
            indent=2
        )

        result: CommitTaskMapperResult = self._call_llm(
            agent_name="CommitTaskMapperAgent",
            folder_name="commit_task_mapping",
            prompt_name="commit_task_mapper_agent",
            variables={
                "commit": commit,
                "tasks": tasks_json,
            },
            response_format=CommitTaskMapperResult,
        )

        return result

    @staticmethod
    def build_pools(tasks: List[ClickUpTask]) -> List[List[ClickUpTask]]:
        """
        Split a list of ClickUp tasks into fixed-size pools for LLM processing.

        This is used to avoid sending too many tasks in a single LLM request,
        improving performance and reducing token usage.

        Args:
            tasks (List[ClickUpTask]): Full list of ClickUp tasks to be split into smaller batches.

        Returns:
            List[List[ClickUpTask]]: A list of task pools, each containing at most `_POOL_SIZE` tasks.
        """
        return [tasks[i:i + CommitTaskMapperAgent._POOL_SIZE] for i in range(0, len(tasks), CommitTaskMapperAgent._POOL_SIZE)]