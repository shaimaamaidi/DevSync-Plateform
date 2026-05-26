"""
Service port for summarizing weekly deployments.

This module defines the IWeeklyDeploymentsSummarizer interface, which specifies
operations for generating a narrative summary from weekly deployment activity.
"""

from abc import ABC, abstractmethod
from typing import List

from backend.src.domain.entities.github.deployment import DeploymentDTO


class IWeeklyDeploymentsSummarizer(ABC):
    """
    Define weekly deployments summarization behavior required by the application.

    This interface represents the contract for analyzing deployment activity
    and generating a human-readable weekly delivery and release summary.
    """

    @abstractmethod
    def summarize_deployments(self, deployments: List[DeploymentDTO]) -> str:
        """
        Generate a narrative summary from weekly deployments.

        Args:
            deployments: List of deployments to summarize.

        Returns:
            str: Human-readable summary describing deployment activity,
                releases, and delivery progress during the week.
        """
        pass