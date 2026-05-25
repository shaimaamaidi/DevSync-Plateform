"""
Service port for unverified completed task inspection via LLMs.

This module defines the IUnverifiedDoneTaskInspector interface,
which specifies operations for analyzing recently completed
ClickUp tasks and determining whether they can be verified
through related GitHub commit activity.

The inspection process helps identify tasks marked as completed
without sufficient implementation evidence.
"""

from abc import abstractmethod, ABC
from typing import List

from backend.src.domain.entities.check_project_status.inspected_unverified_done_task_result import InspectedUnverifiedDoneTaskResult
from backend.src.domain.entities.clickup.list_with_tasks import ClickUpTask
from backend.src.domain.entities.github.commit import CommitDTO




class IUnverifiedDoneTaskInspector(ABC):
    """
    Define unverified completed task inspection behavior required
    by the application.

    This interface represents the contract for analyzing recently
    completed tasks and validating whether their completion is
    supported by GitHub commit activity and LLM-based reasoning.
    """

    @abstractmethod
    def verify_done_tasks(
        self,
        last_done_tasks: List[ClickUpTask],
        commits: List[CommitDTO]
    ) -> List[InspectedUnverifiedDoneTaskResult]:
        """
        Verify completed tasks against GitHub commit activity.

        Args:
            last_done_tasks: List of recently completed ClickUp tasks.
            commits: List of GitHub commits used as verification signals.

        Returns:
            List[InspectedUnverifiedDoneTaskResult]:
                List of completed tasks considered unverified.
        """
        pass