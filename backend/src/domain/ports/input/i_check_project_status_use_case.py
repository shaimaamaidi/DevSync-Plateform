"""
Use case port for project status operations.

This module defines the ICheckProjectStatusUseCase interface, which specifies
operations for computing and retrieving the overall status of a project
based on ClickUp tasks and optional GitHub repository activity.

It acts as the application layer orchestration contract for:
- Aggregating ClickUp task data for a given space
- Integrating GitHub commits and deployments (if available)
- Detecting project activity and stale tasks
- Producing a structured project status summary for the user
"""

from abc import abstractmethod, ABC
from typing import Optional

from backend.src.domain.entities.check_project_status.project_status_summary import ProjectStatusSummary


class ICheckProjectStatusUseCase(ABC):
    """
    Define project status use case behavior required by the application.

    This interface represents the contract for computing the overall status
    of a project by combining ClickUp task data and optional GitHub activity.
    It abstracts the orchestration between infrastructure services, domain
    services, and status computation logic.
    """

    @abstractmethod
    async def get_project_status(self, space_id: str, repo_url: Optional[str]) -> ProjectStatusSummary:
        """
        Compute the project status for a given ClickUp space.

        Args:
            space_id: Identifier of the ClickUp space to analyze.
            repo_url: Optional GitHub repository URL linked to the project.

        Returns:
            ProjectStatusSummary: Structured response containing:
                - Overall project status
                - Task distribution summary
                - GitHub integration indicators (commits/deployments)
                - Activity timestamps
                - Detected stale tasks (if any)
        """
        pass