"""
Service port for task status synthesis via LLMs.

This module defines the ITaskStatusSynthesizerAgent interface, which specifies
operations for synthesizing the status of ClickUp tasks using deployments,
commits, and LLM-based analysis or external services.
"""

from abc import ABC, abstractmethod
from typing import List

from backend.src.domain.entities.checked_task_status.synthesized_task_status_result import SynthesizedTaskStatusResult
from backend.src.domain.entities.clickup.list_with_tasks import ClickUpTask
from backend.src.domain.entities.github.commit import CommitDTO
from backend.src.domain.entities.github.deployment import DeploymentDTO


class ITaskStatusSynthesizer(ABC):
    """
    Define task status synthesis behavior required by the application.

    This interface represents the contract for analyzing deployments,
    commits, and task information in order to synthesize the current
    status of a ClickUp task.
    """

    @abstractmethod
    def synthesize_task_status(
        self,
        task: ClickUpTask,
        deployments: List[DeploymentDTO],
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
            deployments: List of GitHub deployments related to the task repository.
            commits: List of GitHub commits related to the task repository.
            signals: Derived workflow and activity signals generated from
                task lifecycle and GitHub context.

        Returns:
            SynthesizedTaskStatusResult: Structured synthesis result containing:
                - Completion state
                - Confidence level
                - Summary explanation
                - Supporting evidence
        """
        pass