"""
Task status synthesizer agent.

This module defines the TaskStatusSynthesizerAgent, responsible for
analyzing ClickUp tasks using commits and deployments through an LLM.
It synthesizes the current completion status of a task and produces
a structured summary with supporting evidence.
"""

import logging
import json
from typing import List

from backend.src.domain.entities.check_task_status.synthesized_task_status_result import SynthesizedTaskStatusResult
from backend.src.domain.entities.clickup.list_with_tasks import ClickUpTask
from backend.src.domain.entities.github.commit import CommitDTO
from backend.src.domain.entities.github.deployment import DeploymentDTO
from backend.src.domain.ports.services.task_status_check.i_task_status_synthesizer import \
    ITaskStatusSynthesizer
from backend.src.infrastructure.external.shared.agents.base_agent import BaseAgent


logger = logging.getLogger(__name__)


class TaskStatusSynthesizerAgent(BaseAgent[SynthesizedTaskStatusResult], ITaskStatusSynthesizer):
    """
    LLM-based implementation of ITaskStatusSynthesizer.

    This agent is responsible for:
    - Analyzing ClickUp task information
    - Evaluating related commits and deployments
    - Synthesizing task completion status
    - Producing a structured status summary with evidence
    """

    def synthesize_task_status(
        self,
        task: ClickUpTask,
        deployments: List[DeploymentDTO],
        commits: List[CommitDTO]
    ) -> SynthesizedTaskStatusResult:
        """
        Synthesize the status of a ClickUp task using an LLM.

        This method:
        - Serializes task, commit, and deployment data into JSON structures
        - Sends the contextual information to the LLM
        - Parses the LLM response into a structured synthesis result

        Args:
            task: ClickUp task to analyze.
            deployments: List of deployments related to the task.
            commits: List of commits related to the task.

        Returns:
            SynthesizedTaskStatusResult: Synthesized task status containing
                completion state, confidence level, summary,
                and supporting evidence.

        Raises:
            LLMNetworkException: If a network error occurs while contacting the LLM.
            LLMApiException: If the LLM API returns an error response.
            LLMParsingException: If the LLM response cannot be parsed correctly.
        """
        logger.info("Synthesize task status process. task_id=%s.", task.id)

        result: SynthesizedTaskStatusResult = self._call_llm(
            agent_name="TaskStatusSynthesizerAgent",
            folder_name="task_status_check",
            prompt_name="task_status_synthesizer_agent",
            variables={
                "task": json.dumps(task.to_dict(), ensure_ascii=False, indent=2),
                "commits": json.dumps(
                    [c.to_dict() for c in commits],
                    ensure_ascii=False,
                    default=str,
                    indent=2
                ),
                "deployments": json.dumps(
                    [d.model_dump() for d in deployments],
                    ensure_ascii=False,
                    default=str,
                    indent=2
                ),
            },
            response_format=SynthesizedTaskStatusResult,
        )

        if not result:
            logger.warning("No synthesis result returned for task_id=%s.", task.id)

        logger.info("Task status synthesis completed. task_id=%s, is_completed=%s.", task.id, result.is_completed)

        return result