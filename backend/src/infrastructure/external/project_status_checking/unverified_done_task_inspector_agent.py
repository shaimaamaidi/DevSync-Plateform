"""
Unverified done task inspection agent.

This module defines the UnverifiedDoneTaskInspectorAgent, responsible for
analyzing recently completed ClickUp tasks and determining whether they
can be verified through related GitHub commit activity.

It correlates completed task activity with GitHub commits to detect
tasks that may have been marked as done without sufficient technical
implementation evidence.
"""

import asyncio
import logging
import json
from typing import List

from backend.src.domain.entities.checked_project_status.inspected_unverified_done_task_result import \
    InspectedUnverifiedDoneTaskListResult, InspectedUnverifiedDoneTaskResult
from backend.src.domain.entities.clickup.list_with_tasks import ClickUpTask
from backend.src.domain.entities.github.commit import CommitDTO
from backend.src.domain.ports.services.prompt_loading.i_prompt_loader import IPromptLoader
from backend.src.domain.ports.services.project_status_check.unverified_done_task_inspector import \
    IUnverifiedDoneTaskInspector
from backend.src.infrastructure.external.shared.agents.base_agent import BaseAgent


logger = logging.getLogger(__name__)


class UnverifiedDoneTaskInspectorAgent (BaseAgent[InspectedUnverifiedDoneTaskListResult], IUnverifiedDoneTaskInspector):
    """
    LLM-based implementation of IUnverifiedDoneTaskInspector.

    This agent is responsible for:
    - Analyzing recently completed ClickUp tasks
    - Correlating tasks with GitHub commit history
    - Detecting completed tasks without sufficient implementation evidence
    - Producing structured inspection results for further processing
    """

    _TASK_BATCH_SIZE = 10

    def __init__(self, prompt_loader: IPromptLoader):
        """
        Initialize the UnverifiedDoneTaskInspectorAgent.

        Args:
            prompt_loader (IPromptLoader): Service responsible for loading
                prompt templates used by the agent during LLM interactions.
        """
        super().__init__(prompt_loader)

    async def verify_done_tasks(
        self,
        last_done_tasks: List[ClickUpTask],
        commits: List[CommitDTO]
    ) -> List[InspectedUnverifiedDoneTaskResult]:
        """
        Inspect recently completed tasks to verify whether they are
        supported by related GitHub commit activity.

        This method:
        - Serializes completed ClickUp tasks and commits into JSON
        - Sends them to an LLM for analysis
        - Interprets LLM output into structured unverified task results

        Args:
            last_done_tasks: List of recently completed ClickUp tasks.
            commits: List of GitHub commits used as verification signals.

        Returns:
            List[InspectedUnverifiedDoneTaskResult]:
                List of completed tasks considered unverified.

        Raises:
            LLMNetworkException: If a network error occurs while contacting the LLM.
            LLMApiException: If the LLM API returns an error response.
            LLMParsingException: If the LLM response cannot be parsed correctly.
        """
        logger.info("Inspecting unverified done tasks process.")

        commits_payload = [
            {
                "message": c.message[:500],
                "date": c.date.isoformat() if c.date else None,
                "branch": c.branch,
            }
            for c in commits
        ]

        batches = [
            last_done_tasks[i: i + UnverifiedDoneTaskInspectorAgent._TASK_BATCH_SIZE]
            for i in range(0, len(last_done_tasks), UnverifiedDoneTaskInspectorAgent._TASK_BATCH_SIZE)
        ]

        results = await asyncio.gather(
            *[self._verify_batch(batch, commits_payload) for batch in batches]
        )

        unverified_tasks = [task for batch_result in results for task in batch_result if not task.has_commit]

        logger.info(
            "Unverified done task inspecting completed successfully: %d task(s) stales.",
            len(unverified_tasks)
        )

        return unverified_tasks

    async def _verify_batch(
            self,
            tasks_batch: List[ClickUpTask],
            commits_payload: List[dict],
    ) -> List[InspectedUnverifiedDoneTaskResult]:
        """
        Run LLM verification on a single batch of recently done tasks.

        Args:
            tasks_batch: Subset of recently completed tasks to verify.
            commits_payload: Pre-projected commit list shared across all batches.

        Returns:
            List[InspectedUnverifiedDoneTaskResult]: Unverified tasks detected in this batch.
        """
        tasks_payload = json.dumps(
            [{"id": t.id, "name": t.name, "description": t.description} for t in tasks_batch],
            ensure_ascii=False,
        )

        parsed: InspectedUnverifiedDoneTaskListResult = self._call_llm(
            agent_name="UnverifiedDoneTaskInspectorAgent",
            folder_name="project_status_checking",
            prompt_name="unverified_done_tasks_inspector_agent",
            variables={
                "tasks": tasks_payload,
                "commits": commits_payload,
            },
            response_format=InspectedUnverifiedDoneTaskListResult,
        )

        if not parsed or not parsed.tasks:
            logger.debug(
                "Batch of %d task(s): all verified.",
                len(tasks_batch),
            )
            return []

        return parsed.tasks