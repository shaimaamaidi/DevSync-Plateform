"""
Service port for GitHub repository validation.

This module defines the IGitHubRepoValidationService interface,
which specifies operations related to validating the existence
and accessibility of GitHub repositories.
"""

from abc import ABC, abstractmethod


class IGitHubRepoValidationService(ABC):
    """
    Define GitHub repository validation behavior required by the application.

    This interface represents the contract for validating whether
    a GitHub repository exists and is accessible through the GitHub API.
    """

    @abstractmethod
    async def verify_exists(self, url: str) -> bool:
        """
        Verify that a GitHub repository exists and is accessible.

        Args:
            url: Full GitHub repository URL.

        Returns:
            True if the repository exists and is accessible.
        """
        pass