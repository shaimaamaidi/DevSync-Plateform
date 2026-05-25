"""
Unverified done task inspection agent.

This module defines the UnverifiedDoneTaskInspectorAgent, responsible for
analyzing recently completed ClickUp tasks and determining whether they
can be verified through related GitHub commit activity.

It correlates completed task activity with GitHub commits to detect
tasks that may have been marked as done without sufficient technical
implementation evidence.
"""

import logging
import json
from typing import List

from backend.src.domain.entities.check_project_status.inspected_unverified_done_task_result import \
    InspectedUnverifiedDoneTaskListResult, InspectedUnverifiedDoneTaskResult
from backend.src.domain.entities.clickup.list_with_tasks import ClickUpTask
from backend.src.domain.entities.github.commit import CommitDTO
from backend.src.domain.ports.services.iprompt_loader import IPromptLoader
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

    def __init__(self, prompt_loader: IPromptLoader):
        """
        Initialize the UnverifiedDoneTaskInspectorAgent.

        Args:
            prompt_loader (IPromptLoader): Service responsible for loading
                prompt templates used by the agent during LLM interactions.
        """
        super().__init__(prompt_loader)

    def verify_done_tasks(
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

        tasks_json = json.dumps(
            [task.to_dict() for task in last_done_tasks],
            ensure_ascii=False,
            indent=2
        )

        parsed: InspectedUnverifiedDoneTaskListResult = self._call_llm(
            agent_name="UnverifiedDoneTaskInspectorAgent",
            folder_name="project_status_check",
            prompt_name="unverified_done_tasks_inspector_agent",
            variables={
                "tasks": tasks_json,
                "commits": json.dumps(
                    [c.to_dict() for c in commits],
                    ensure_ascii=False,
                    default=str,
                    indent=2
                )
            },
            response_format=InspectedUnverifiedDoneTaskListResult,
        )

        if not parsed or not parsed.tasks:
            logger.warning("All recently done tasks are verified.")
            return []

        logger.info(
            "Unverified done task inspecting completed successfully: %d task(s) stales.",
            len(parsed.tasks)
        )

        return parsed.tasks