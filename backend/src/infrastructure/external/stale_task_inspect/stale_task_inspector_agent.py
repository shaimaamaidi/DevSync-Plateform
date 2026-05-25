"""
Stale task inspection agent.

This module defines the StaleTaskInspectorAgent, responsible for analyzing
ClickUp tasks that are currently in progress and determining whether they
are stale or blocked based on commit history and LLM reasoning.

It correlates task activity with GitHub commits to detect inactivity
patterns and potential blocking issues.
"""

import logging
import json
from typing import List

from backend.src.domain.entities.check_project_status.inspected_stale_task_result import InspectedStaleTaskResult, \
    InspectedStaleTaskListResult
from backend.src.domain.entities.clickup.list_with_tasks import ClickUpTask
from backend.src.domain.entities.github.commit import CommitDTO
from backend.src.domain.ports.services.iprompt_loader import IPromptLoader
from backend.src.domain.ports.services.stale_task_inspection.stale_task_inspector import IStaleTaskInspector
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

    def __init__(self, prompt_loader: IPromptLoader):
        """
        Initialize the StaleTaskInspectorAgent.

        Args:
            prompt_loader (IPromptLoader): Service responsible for loading
                prompt templates used by the agent during LLM interactions.
        """
        super().__init__(prompt_loader)

    def inspect_stale_tasks(
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

        tasks_json = json.dumps(
            [task.to_dict() for task in tasks_in_progress],
            ensure_ascii=False,
            indent=2
        )

        parsed: InspectedStaleTaskListResult = self._call_llm(
            agent_name="StaleTaskInspectorAgent",
            folder_name="tasks_stale_inspection",
            prompt_name="tasks_stale_inspector_agent",
            variables={
                "tasks": tasks_json,
                "commits": json.dumps(
                    [c.to_dict() for c in commits],
                    ensure_ascii=False,
                    default=str,
                    indent=2
                )
            },
            response_format=InspectedStaleTaskListResult,
        )

        if not parsed or not parsed.tasks:
            logger.warning("No tasks stales.")
            return []

        logger.info(
            "Task inspecting completed successfully: %d task(s) stales.",
            len(parsed.tasks)
        )

        return parsed.tasks