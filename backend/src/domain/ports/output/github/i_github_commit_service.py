"""
Service port for GitHub commit integrations.

This module defines the IGitHubCommitService interface, which specifies operations for interacting
with GitHub in order to retrieve commit-related data from repositories.
"""

from abc import ABC, abstractmethod
from typing import List

from backend.src.domain.entities.github.commit import CommitDTO


class IGitHubCommitService(ABC):
    """
    Define GitHub commit service behavior required by the application.

    This interface represents the contract for retrieving commit information from GitHub
    repositories in a standardized way for downstream processing and analysis.
    """

    @abstractmethod
    async def get_commits(self, repo_url: str, max_commits: int = 100) -> List[CommitDTO]:
        """
        Fetch commits for a GitHub repository.

        Args:
            repo_url (str): GitHub repository URL.
            max_commits (int): Maximum number of commits to retrieve.

        Returns:
            List[CommitDTO]: List of commit data transfer objects.
        """
        pass