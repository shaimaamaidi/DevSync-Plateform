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

from backend.src.domain.entities.checked_task_status.synthesized_task_status_result import SynthesizedTaskStatusResult
from backend.src.domain.entities.clickup.list_with_tasks import ClickUpTask
from backend.src.domain.entities.github.commit import CommitDTO
from backend.src.domain.ports.services.prompt_loading.i_prompt_loader import IPromptLoader
from backend.src.domain.ports.services.task_status_checking.i_task_status_synthesizer import ITaskStatusSynthesizer
from backend.src.infrastructure.external.shared.agents.base_agent import BaseAgent


logger = logging.getLogger(__name__)


class TaskStatusSynthesizerAgent(BaseAgent[SynthesizedTaskStatusResult], ITaskStatusSynthesizer):
    """
    LLM-based implementation of ITaskStatusSynthesizer.

    This agent is responsible for:
    - Analyzing ClickUp task metadata and lifecycle information
    - Evaluating related GitHub commits and deployments
    - Interpreting derived workflow and activity signals
    - Synthesizing the current task completion status
    - Producing a structured status summary with supporting evidence

    The agent leverages an LLM to correlate task state, development
    activity, and deployment evidence in order to estimate the real
    implementation progress of a task.
    """

    def __init__(self, prompt_loader: IPromptLoader):
        """
        Initialize the TaskStatusSynthesizerAgent.

        Args:
            prompt_loader (IPromptLoader): Service responsible for loading
                prompt templates used by the agent during LLM interactions.
        """
        super().__init__(prompt_loader)

    def synthesize_task_status(
        self,
        task: ClickUpTask,
        commits: List[CommitDTO],
        signals: dict
    ) -> SynthesizedTaskStatusResult:
        """
        Synthesize the implementation status of a ClickUp task using an LLM.

        This method:
        - Serializes task, commit, deployment, and derived signal data
        - Sends the contextual information to the LLM
        - Interprets the returned analysis into a structured synthesis result

        The synthesis process combines:
        - Task metadata and status
        - Git commit activity
        - Deployment history
        - Derived workflow signals

        to estimate the actual completion state of the task.

        Args:
            task: ClickUp task to analyze.
            commits: List of GitHub commits related to the task repository.
            signals: Derived workflow and activity signals generated from
                task lifecycle and GitHub context.

        Returns:
            SynthesizedTaskStatusResult: Structured synthesis result containing:
                - Completion state
                - Confidence level
                - Summary explanation
                - Supporting evidence

        Raises:
            LLMNetworkException: If a network error occurs while contacting the LLM.
            LLMApiException: If the LLM API returns an error response.
            LLMParsingException: If the LLM response cannot be parsed correctly.
        """
        logger.info("Synthesize task status process. task_id=%s.", task.id)

        result: SynthesizedTaskStatusResult = self._call_llm(
            agent_name="TaskStatusSynthesizerAgent",
            folder_name="task_status_checking",
            prompt_name="task_status_synthesizer_agent",
            variables={
                "task": json.dumps(task.to_dict(), ensure_ascii=False, indent=2),
                "signals": json.dumps(signals, ensure_ascii=False, indent=2),
                "commits": [{
                    "message": c.message[:1000],
                    "date": c.date.isoformat() if c.date else None,
                    "branch": c.branch
                } for c in commits],
            },
            response_format=SynthesizedTaskStatusResult,
        )

        if not result:
            logger.warning("No synthesis result returned for task_id=%s.", task.id)
            return SynthesizedTaskStatusResult(
                is_completed=task.status in ("complete", "done") if task.status else False,
                confidence="low",
                summary=f"No synthesis result returned — based on ClickUp status only: '{task.status}'.",
                evidence=[f"No GitHub activity found — analysis based on ClickUp status only. Status is '{task.status}'."]
            )

        logger.info("Task status synthesis completed. task_id=%s, is_completed=%s.", task.id, result.is_completed)

        return result