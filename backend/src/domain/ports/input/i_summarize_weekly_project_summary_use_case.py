"""
Use case port for weekly project summary operations.

This module defines the ISummarizeWeeklyProjectUseCase interface, which specifies
operations for generating a weekly project summary based on ClickUp tasks and
GitHub activity (commits and deployments).

It acts as the application layer orchestration contract for:
- Collecting ClickUp tasks for a given workspace
- Retrieving GitHub commits and deployments (if repository is linked)
- Delegating summarization to domain services
- Producing a structured weekly project summary response
"""

from abc import ABC, abstractmethod
from typing import Optional

from backend.src.domain.entities.weekly_project_summary.weekly_project_summary_response import WeeklyProjectSummaryResponse


class ISummarizeWeeklyProjectUseCase(ABC):
    """
    Define weekly project summary use case behavior required by the application.

    This interface represents the contract for generating a consolidated
    weekly report of project activity by combining ClickUp task data with
    GitHub commits and deployments. It abstracts orchestration between
    infrastructure services, domain services, and LLM-based summarizers.
    """

    @abstractmethod
    async def get_weekly_project_summary(
        self,
        space_id: str,
        repo_url: Optional[str],
    ) -> WeeklyProjectSummaryResponse:
        """
        Generate a weekly project summary for a given ClickUp space.

        Args:
            space_id: Identifier of the ClickUp space to analyze.
            repo_url: Optional GitHub repository URL linked to the project.

        Returns:
            WeeklyProjectSummaryResponse: Structured weekly report containing
                task activity, commits, deployments, and generated summaries.
        """
        pass