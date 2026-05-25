"""
Service port for task status synthesis via LLMs.

This module defines the ITaskStatusSynthesizerAgent interface, which specifies
operations for synthesizing the status of ClickUp tasks using deployments,
commits, and LLM-based analysis or external services.
"""

from abc import ABC, abstractmethod
from typing import List

from backend.src.domain.entities.check_task_status.synthesized_task_status_result import SynthesizedTaskStatusResult
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
        Synthesize the status of a task based on deployments and commits.

        Args:
            task: ClickUp task to analyze.
            deployments: List of deployments related to the task.
            commits: List of commits related to the task.

        Returns:
            SynthesizedTaskStatusResult: Synthesized task status result
                containing completion state, confidence level,
                summary, and supporting evidence.
        """
        pass