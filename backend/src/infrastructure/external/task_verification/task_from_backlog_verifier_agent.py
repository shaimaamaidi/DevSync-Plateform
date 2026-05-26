"""
ClickUp task verifier agent.

This module defines the TaskFromBacklogVerifierAgent class, responsible for
verifying generated ClickUp tasks from a sprint backlog against existing
ClickUp tasks using an LLM. It ensures that only meaningful create or update
actions are returned based on detected differences.

This agent specializes the generic BaseTaskVerifierAgent for backlog-generated
tasks
"""

import logging
import json
from typing import List

from backend.src.domain.entities.clickup.list_with_tasks import ClickUpTask
from backend.src.domain.entities.generated_tasks.generated_task_from_backlog import GeneratedTaskFromBacklog
from backend.src.domain.entities.verified_tasks.verified_task_from_backlog import VerifiedTaskFromBacklog, \
    VerifiedTaskListFromBacklog
from backend.src.domain.ports.services.prompt_loading.i_prompt_loader import IPromptLoader
from backend.src.domain.ports.services.task_verification.i_task_from_backlog_verifier import \
    ITaskFromBacklogVerifier
from backend.src.infrastructure.external.task_verification.base_task_verifier_agent import BaseTaskVerifierAgent


logger = logging.getLogger(__name__)


class TaskFromBacklogVerifierAgent(
    BaseTaskVerifierAgent[GeneratedTaskFromBacklog, VerifiedTaskFromBacklog, VerifiedTaskListFromBacklog],
    ITaskFromBacklogVerifier
):
    """
    LLM-based implementation of ITaskFromBacklogVerifier.

    This agent is responsible for:
    - Verifying generated backlog tasks against existing ClickUp tasks
    - Identifying create and update actions
    - Filtering redundant updates without effective changes
    - Serializing generated tasks for LLM verification
    """

    def __init__(self, prompt_loader: IPromptLoader):
        """
        Initialize the backlog task verifier agent.

        Args:
            prompt_loader: Service used to load prompt templates.
        """
        super().__init__(
            prompt_loader=prompt_loader,
            agent_name="TaskFromBacklogVerifierAgent",
            folder_name="task_from_backlog_verification",
            prompt_name="task_from_backlog_verifier_agent",
            response_format=VerifiedTaskListFromBacklog,
        )

    def _serialize_generated(self, tasks: List[GeneratedTaskFromBacklog]) -> str:
        """
        Serialize generated backlog tasks into a JSON string.

        Prepares generated tasks for LLM verification by converting them into
        a structured JSON representation.

        Args:
            tasks: Generated backlog tasks to serialize.

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
                    "estimation": t.estimation,
                }
                for t in tasks
            ],
            ensure_ascii=False,
            indent=2,
        )

    def _has_effective_changes(
        self,
        result: VerifiedTaskFromBacklog,
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
            TaskFromBacklogVerifierAgent._status_changed(result, existing),
            TaskFromBacklogVerifierAgent._priority_changed(result, existing),
            TaskFromBacklogVerifierAgent._assignee_changed(result, existing),
            result.estimation != existing.estimation,
        ])
