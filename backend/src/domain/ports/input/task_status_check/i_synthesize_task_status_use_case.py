"""
Use case port for task status synthesis operations.

This module defines the ISynthesizeTaskStatusUseCase interface, which specifies
operations for analyzing and synthesizing the status of ClickUp tasks using
external context such as repository information, commits, and deployments.

It acts as the application layer orchestration contract for:
- Analyzing task completion state
- Enriching task status using repository data
- Delegating synthesis logic to domain/LLM agents
"""

from abc import ABC, abstractmethod
from typing import Optional

from backend.src.domain.entities.checked_task_status.synthesized_task_status_result import SynthesizedTaskStatusResult
from backend.src.domain.entities.clickup.list_with_tasks import ClickUpTask


class ISynthesizeTaskStatusUseCase(ABC):
    """
    Define task status synthesis use case behavior required by the application.

    This interface represents the contract for analyzing a ClickUp task
    and producing a synthesized status based on available context such as
    repository information and related execution data.
    """

    @abstractmethod
    async def analyze_task_status(
        self,
        repo_url: Optional[str],
        task: ClickUpTask
    ) -> SynthesizedTaskStatusResult:
        """
        Analyze and synthesize the status of a ClickUp task.

        Args:
            repo_url: Optional URL of the repository associated with the task.
            task: ClickUp task to analyze.

        Returns:
            SynthesizedTaskStatusResult: Synthesized result containing completion
                status, confidence level, summary, and supporting evidence.
        """
        pass