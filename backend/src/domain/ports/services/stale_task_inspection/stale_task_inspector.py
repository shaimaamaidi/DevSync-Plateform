"""
Service port for stale task inspection via LLMs.

This module defines the IStaleTaskInspector interface, which specifies
operations for analyzing ClickUp tasks and detecting whether they are
stale or blocked based on commit history and external signals.
"""

from abc import ABC, abstractmethod
from typing import List

from backend.src.domain.entities.check_project_status.inspected_stale_task_result import InspectedStaleTaskResult
from backend.src.domain.entities.clickup.list_with_tasks import ClickUpTask
from backend.src.domain.entities.github.commit import CommitDTO


class IStaleTaskInspector(ABC):
    """
    Define stale task inspection behavior required by the application.

    This interface represents the contract for analyzing in-progress tasks
    and detecting stagnation or blocking states using LLM-based reasoning
    and commit activity correlation.
    """

    @abstractmethod
    def inspect_stale_tasks(
        self,
        tasks: List[ClickUpTask],
        commits: List[CommitDTO]
    ) -> List[InspectedStaleTaskResult]:
        """
        Inspect tasks to detect stale or blocked states.

        Args:
            tasks: List of ClickUp tasks to analyze.
            commits: List of GitHub commits used as activity signals.

        Returns:
            List[InspectedStaleTaskResult]: List of detected stale task results.
        """
        pass