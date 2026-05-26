"""
Commit-to-task mapping agent.

This module defines the CommitTaskMapperAgent, responsible for analyzing
GitHub commit messages and mapping them to the most relevant ClickUp tasks.

It uses LLM-based reasoning to:
- Interpret commit semantics and intent
- Compare commits against available ClickUp tasks
- Identify the best matching task for a given commit
- Support traceability between GitHub activity and task management systems

This component is part of the project status tracking pipeline, enabling
cross-referencing between development activity and task execution in ClickUp.
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

    This agent is responsible for:
    - Mapping a GitHub commit to the most relevant ClickUp task
    - Analyzing semantic relationships between commit messages and tasks
    - Using LLM reasoning to identify the best matching task
    - Returning a structured ClickUpTask if a match is found
    """

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
        Map a GitHub commit to its corresponding ClickUp task.

        This method:
        - Serializes available ClickUp tasks into JSON
        - Sends the commit and tasks to an LLM for matching
        - Returns the most relevant task if found

        Args:
            commit: The GitHub commit message or identifier to analyze.
            tasks: List of ClickUp tasks available for matching.

        Returns:
            Optional[ClickUpTask]: The matched task if found, otherwise None.

        Raises:
            LLMNetworkException: If a network error occurs while contacting the LLM.
            LLMApiException: If the LLM API returns an error response.
            LLMParsingException: If the LLM response cannot be parsed correctly.
        """

        logger.info("Mapping commit to task process.")

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

        if not result:
            logger.warning("No task found for the commit: %s.", commit)
            return None

        all_tasks = {task.id: task for task in tasks}

        matched_task = all_tasks.get(result.id)

        if not matched_task:
            logger.warning("Task id returned by LLM not found in input tasks. id=%s.", result.ids[0])
            return None

        logger.info(
            "Commit to task mapping completed successfully: task_id=%s.",
            matched_task.id,
        )

        return matched_task