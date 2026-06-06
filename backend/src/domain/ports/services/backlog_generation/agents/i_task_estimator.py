"""
Service port for task estimation.

This module defines the ITaskEstimator interface, which specifies operations
for estimating effort of user stories within an epic and producing
sprint-ready user story structures.
"""

from abc import ABC, abstractmethod
from typing import List

from backend.src.domain.entities.backlog.structure import EpicBacklog
from backend.src.domain.entities.sprint.sprint import UserStorySprint


class ITaskEstimator(ABC):
    """
    Define task estimation behavior required by the application.

    This interface is responsible for:
    - Estimating effort for user stories within an epic
    - Producing structured sprint-ready user stories
    - Using contextual information to improve estimation accuracy
    - Supporting sprint planning and workload prediction

    The estimation process may rely on:
    - LLM-based reasoning
    - historical context
    - product and market intelligence inputs
    """

    @abstractmethod
    def estimate_tasks(
        self,
        context: str,
        epic: EpicBacklog,
    ) -> List[UserStorySprint]:
        """
        Estimate tasks and effort for all user stories in an epic.

        This method transforms raw user stories into sprint-ready structures
        enriched with task breakdowns and effort estimation.

        Args:
            context (str): Global or product context used to improve estimation accuracy.
            epic (EpicBacklog): Epic containing user stories to estimate.

        Returns:
            List[UserStorySprint]: List of estimated user stories, each containing:
                - decomposed tasks
                - estimated effort
                - sprint-ready structure
        """
        pass