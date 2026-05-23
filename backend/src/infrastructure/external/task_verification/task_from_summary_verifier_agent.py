"""
ClickUp task verifier agent.

This module defines the TaskFromSummaryVerifierAgent class, responsible for
verifying generated ClickUp tasks from a summary against existing ClickUp
tasks using an LLM. It ensures that only meaningful create or update actions
are returned based on detected differences.

This agent specializes the generic BaseTaskVerifierAgent for summary-generated
tasks.
"""

import logging
import json
from typing import List

from backend.src.domain.entities.clickup.list_with_tasks import ClickUpTask
from backend.src.domain.entities.generated_tasks.generated_task_from_summary import GeneratedTaskFromSummary
from backend.src.domain.entities.verified_tasks.verified_task_from_summary import VerifiedTaskFromSummary, VerifiedTaskListFromSummary
from backend.src.domain.ports.services.iprompt_loader import IPromptLoader
from backend.src.domain.ports.services.task_verification.i_task_from_summary_verifier import ITaskFromSummaryVerifier
from backend.src.infrastructure.external.task_verification.base_task_verifier_agent import BaseTaskVerifierAgent


logger = logging.getLogger(__name__)


class TaskFromSummaryVerifierAgent(
    BaseTaskVerifierAgent[GeneratedTaskFromSummary, VerifiedTaskFromSummary, VerifiedTaskListFromSummary],
    ITaskFromSummaryVerifier):
    """
    LLM-based implementation of ITaskFromSummaryVerifier.

    This agent is responsible for:
    - Verifying generated summary tasks against existing ClickUp tasks
    - Identifying create and update actions
    - Filtering redundant updates without effective changes
    - Serializing generated tasks for LLM verification
    """

    def __init__(self, prompt_loader: IPromptLoader):
        """
        Initialize the summary task verifier agent.

        Args:
            prompt_loader: Service used to load prompt templates.
        """
        super().__init__(
            prompt_loader=prompt_loader,
            agent_name="TaskFromSummaryVerifierAgent",
            folder_name="task_from_summary_verification",
            prompt_name="task_from_summary_verifier_agent",
            response_format=VerifiedTaskListFromSummary,
        )

    def _serialize_generated(self, tasks: List[GeneratedTaskFromSummary]) -> str:
        """
        Serialize generated summary tasks into a JSON string.

        Prepares generated tasks for LLM verification by converting them into
        a structured JSON representation.

        Args:
            tasks: Generated summary tasks to serialize.

        Returns:
            JSON representation of generated tasks.
        """
        return json.dumps(
            [
                {
                    "task_name": t.task_name,
                    "task_description": t.task_description,
                    "task_status": t.task_status,
                    "task_priority": t.task_priority,
                    "task_assigne": t.task_assigne,
                    "location": t.location,
                }
                for t in tasks
            ],
            ensure_ascii=False,
            indent=2,
        )



    def _has_effective_changes(
        self,
        result: VerifiedTaskFromSummary,
        existing: ClickUpTask,
    ) -> bool:
        """
        Determine whether a verified update contains effective changes.

        Compares the verified task result against the existing ClickUp task
        to detect meaningful modifications.

        Args:
            result: Verified task result returned by the LLM.
            existing: Existing ClickUp task.

        Returns:
            True if at least one meaningful field changed, otherwise False.
        """
        return any([
            TaskFromSummaryVerifierAgent._status_changed(result, existing),
            TaskFromSummaryVerifierAgent._priority_changed(result, existing),
            TaskFromSummaryVerifierAgent._assignee_changed(result, existing),
        ])