"""
Stale task inspection agent.

This module defines the StaleTaskInspectorAgent, responsible for analyzing
ClickUp tasks that are currently in progress and determining whether they
are stale or blocked based on commit history and LLM reasoning.

It correlates task activity with GitHub commits to detect inactivity
patterns and potential blocking issues.
"""

import asyncio
import logging
import json
from typing import List

from backend.src.domain.entities.checked_project_status.inspected_stale_task_result import InspectedStaleTaskResult, \
    InspectedStaleTaskListResult
from backend.src.domain.entities.clickup.list_with_tasks import ClickUpTask
from backend.src.domain.entities.github.commit import CommitDTO
from backend.src.domain.ports.services.prompt_loading.i_prompt_loader import IPromptLoader
from backend.src.domain.ports.services.project_status_check.stale_task_inspector import IStaleTaskInspector
from backend.src.infrastructure.external.shared.agents.base_agent import BaseAgent


logger = logging.getLogger(__name__)


class StaleTaskInspectorAgent (BaseAgent[InspectedStaleTaskListResult], IStaleTaskInspector):
    """
    LLM-based implementation of IStaleTaskInspector.

    This agent is responsible for:
    - Analyzing in-progress ClickUp tasks
    - Correlating tasks with GitHub commit history
    - Detecting stale or blocked tasks using LLM reasoning
    - Producing structured inspection results for further processing
    """

    _TASK_BATCH_SIZE = 10

    def __init__(self, prompt_loader: IPromptLoader):
        """
        Initialize the StaleTaskInspectorAgent.

        Args:
            prompt_loader (IPromptLoader): Service responsible for loading
                prompt templates used by the agent during LLM interactions.
        """
        super().__init__(prompt_loader)

    async def inspect_stale_tasks(
        self,
        tasks_in_progress: List[ClickUpTask],
        commits: List[CommitDTO]
    ) -> List[InspectedStaleTaskResult]:
        """
        Inspect in-progress tasks to detect whether they are stale or blocked.

        This method:
        - Serializes ClickUp tasks and commits into JSON
        - Sends them to an LLM for analysis
        - Interprets LLM output into structured stale task results

        Args:
            tasks_in_progress: List of ClickUp tasks currently in progress.
            commits: List of GitHub commits used as activity signals.

        Returns:
            List[InspectedStaleTaskResult]: List of detected stale/blocked tasks.

        Raises:
            LLMNetworkException: If a network error occurs while contacting the LLM.
            LLMApiException: If the LLM API returns an error response.
            LLMParsingException: If the LLM response cannot be parsed correctly.
        """
        logger.info("Inspecting stale tasks process.")

        commits_payload = [
            {
                "message": c.message[:500],
                "date": c.date.isoformat() if c.date else None,
                "branch": c.branch,
            }
            for c in commits
        ]

        batches = [
            tasks_in_progress[i: i + StaleTaskInspectorAgent._TASK_BATCH_SIZE]
            for i in range(0, len(tasks_in_progress), StaleTaskInspectorAgent._TASK_BATCH_SIZE)
        ]

        results = await asyncio.gather(
            *[self._inspect_batch(batch, commits_payload) for batch in batches]
        )

        stale_tasks = [task for batch_result in results for task in batch_result if task.is_blocked]

        if not stale_tasks:
            logger.warning("All tasks are in a real progress.")
            return []

        logger.info(
            "Stale task inspecting completed successfully: %d task(s) stales.",
            len(stale_tasks)
        )

        return stale_tasks

    async def _inspect_batch(
            self,
            tasks_batch: List[ClickUpTask],
            commits_payload: List[dict],
    ) -> List[InspectedStaleTaskResult]:
        """
        Run LLM inspection on a single batch of tasks.

        Args:
            tasks_batch: Subset of in-progress tasks to analyze.
            commits_payload: Pre-projected commit list shared across all batches.

        Returns:
            List[InspectedStaleTaskResult]: Stale tasks detected in this batch.
        """
        tasks_payload = json.dumps(
            [{"id": t.id, "name": t.name, "description": t.description} for t in tasks_batch],
            ensure_ascii=False,
        )

        parsed: InspectedStaleTaskListResult = self._call_llm(
            agent_name="StaleTaskInspectorAgent",
            folder_name="project_status_checking",
            prompt_name="stale_tasks_inspector_agent",
            variables={
                "tasks": tasks_payload,
                "commits": commits_payload,
            },
            response_format=InspectedStaleTaskListResult,
        )

        if not parsed or not parsed.tasks:
            logger.debug(
                "Batch of %d task(s): no stale tasks detected.",
                len(tasks_batch),
            )
            return []

        return parsed.tasks