"""
Service port for GitHub integrations.

This module defines the IGitHubService interface, which specifies operations for interacting
with GitHub, such as fetching deployments and other repository-related data.
"""

from abc import ABC, abstractmethod
from typing import List
from datetime import datetime

from backend.src.domain.entities.github.deployment import DeploymentDTO


class IGitHubDeploymentService(ABC):
    """
    Define GitHub service behavior required by the application.

    This interface represents the contract for interacting with GitHub APIs in order to
    retrieve repository-related information such as deployments.
    """

    @abstractmethod
    async def get_deployments(self, repo_url: str) -> List[DeploymentDTO]:
        """
        Fetch deployments for a GitHub repository.

        Args:
            repo_url (str): GitHub repository URL.

        Returns:
            List[DeploymentDTO]: List of deployment data transfer objects.
        """
        pass

    @abstractmethod
    async def get_deployments_between_dates(
        self,
        repo_url: str,
        since: datetime,
        until: datetime,
        max_deployments: int ,
    ) -> List[DeploymentDTO]:
        """
        Retrieve deployments within a date range.

        Strategy (mirrors get_commits_between_dates):
            - Paginate API + Actions newest-first
            - Stop pagination as soon as created_at goes below `since`
            - Apply max_deployments cap AFTER date filtering

        Args:
            repo_url: GitHub repository URL.
            since: Start datetime (inclusive).
            until: End datetime (inclusive).
            max_deployments: Maximum to return after date filtering.
                Defaults to DEPLOYMENTS_MAX_ITEMS.

        Returns:
            List[DeploymentDTO]: Deployments in [since, until], newest first.
        """
        pass